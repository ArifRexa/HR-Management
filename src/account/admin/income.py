from django.contrib import admin, messages
from django.db import models
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce
from django.forms import Textarea
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html
from django.core.mail import EmailMessage, EmailMultiAlternatives
from account.models import Income
from account.services.balance import BalanceSummery

from config.settings import STATIC_ROOT
from config.utils.pdf import PDF
from project_management.models import Client


class ActiveClientFilter(admin.SimpleListFilter):
    title = "Client"
    parameter_name = "project__client__id"

    def lookups(self, request, model_admin):
        clients = Client.objects.filter(project__active=True).distinct()
        return tuple((client.pk, client.name) for client in list(clients))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(project__client__id=self.value())
        return queryset

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "date",
        "hours",
        "hour_rate",
        "convert_rate",
        "payment_details",
        "status_col",
    )
    date_hierarchy = "date"
    exclude = ["is_send_clients"]
    readonly_fields = ("payment",)
    list_filter = [
        "status",
        "project",
        "project__client__payment_method",
        ActiveClientFilter,  
    ]
    actions = [
        "approve_selected",
        "pending_selected",
        "print_income_invoices",
        "send_income_invoices_email",
    ]
    # list_editable = ('status',)
    formfield_overrides = {models.TextField: {"widget": Textarea(attrs={"rows": 2})}}
    autocomplete_fields = ["project"]

    change_list_template = "admin/income/list.html"

    list_per_page = 20
    
    def get_list_filter(self, request):
        if request.user.has_perm("project_management.view_client"):
            return super().get_list_filter(request)
        self.list_filter.remove("project__client__payment_method")
        return self.list_filter

    @admin.action(description="Status")
    def status_col(self, obj):
        color = "red"
        if obj.status == "approved":
            color = "green"
        return format_html(f'<b style="color: {color}">{obj.get_status_display()}</b>')

    @admin.display()
    def payment_details(self, obj):
        return format_html(
            f"<b style='color: green; font-size: 16px'>$ {obj.payment / obj.convert_rate}</b> / "
            f"{obj.payment} TK"
        )

    def get_total_hour(self, request):
        filters = dict(
            [
                (key, request.GET.get(key))
                for key in dict(request.GET)
                if key not in ["p", "o"]
            ]
        )
        if not request.user.is_superuser:
            filters["created_by__id__exact"] = request.user.employee.id
        dataset = Income.objects.filter(
            *[Q(**{key: value}) for key, value in filters.items() if value]
        )
        return {
            "total_pending": dataset.filter(status="pending").aggregate(
                total=Coalesce(Sum("payment"), 0.0)
            )["total"],
            "total_pending_usd": dataset.filter(status="pending").aggregate(
                total=Coalesce(Sum(F("payment") / F("convert_rate")), 0.0)
            )["total"],
            "total_paid": dataset.filter(status="approved").aggregate(
                total=Coalesce(Sum("payment"), 0.0)
            )["total"],
            "total_paid_usd": dataset.filter(status="approved").aggregate(
                total=Coalesce(Sum(F("payment") / F("convert_rate")), 0.0)
            )["total"],
            "pending_hour": dataset.filter(status="pending").aggregate(
                total=Coalesce(Sum("hours"), 0.0)
            )["total"],
            "approved_hour": dataset.filter(status="approved").aggregate(
                total=Coalesce(Sum("hours"), 0.0)
            )["total"],
            "total_loss_hours": dataset.aggregate(
                total=Coalesce(Sum("loss_hours"), 0.0)
            )["total"],
        }

    def changelist_view(self, request, extra_context=None):
        my_context = {
            "result": self.get_total_hour(request),
        }
        return super().changelist_view(request, extra_context=my_context)

    @admin.action()
    def approve_selected(self, request, queryset):
        queryset.update(status="approved")
        # self.message_user(request, f'Status has been updated to approved for {len(queryset)} items', messages.SUCCESS)

    @admin.action()
    def pending_selected(self, request, queryset):
        queryset.update(status="pending")
        # self.message_user(request, f'Status has been updated to pending for {len(queryset)} items', messages.SUCCESS)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "balance/",
                self.admin_site.admin_view(self.balance_view),
                name="account_balance",
            ),
        ]
        return my_urls + urls

    def balance_view(self, request, *args, **kwargs):
        if request.user.is_superuser:
            balance = (BalanceSummery()).get_context_data()
            context = dict(
                self.admin_site.each_context(request),
                data=balance,
                title=f"Profit / Loss",
            )
            return TemplateResponse(request, "admin/balance/balance.html", context)
        raise PermissionDenied

    @admin.action()
    def print_income_invoices(self, request, queryset):
        queryset = queryset.order_by("date")
        income_list = queryset.values_list("id", flat=True)
        id_str = "_".join(list(map(str, income_list)))
        project_name = queryset.first().project.title
        pdf = PDF()
        pdf.file_name = f"Income Invoice-{project_name}-{id_str}"
        pdf.template_path = "compliance/new_income_invoice.html"
        protocal = "https" if request.is_secure() else "http"
        invoice_total = (
            queryset.values("date", "hour_rate")
            .annotate(project_total=F("hours") * F("hour_rate"))
            .aggregate(total=Sum("project_total"))
        )
        pdf.context = {
            "invoices": queryset,
            "seal": f"{STATIC_ROOT}/stationary/sign_md.png",
            "host": f"{protocal}://{request.get_host()}",
            "invoice_total": invoice_total.get("total"),
        }
        return pdf.render_to_pdf(download=True)

    @admin.action()
    def send_income_invoices_email(self, request, queryset):
        queryset = queryset.order_by("date")
        income_list = queryset.values_list("id", flat=True)
        income_date_list = queryset.values_list("date", flat=True)
        income_date_list_str = "|".join(list(map(str, income_date_list)))
        id_str = "|".join(list(map(str, income_list)))
        project_name = queryset.first().project.title
        client = queryset.first().project.client

        pdf = PDF()
        pdf.file_name = f"Income Invoice-{project_name}-{id_str}"
        pdf.template_path = "compliance/new_income_invoice.html"
        protocal = "https" if request.is_secure() else "http"
        invoice_total = (
            queryset.values("date", "hour_rate")
            .annotate(project_total=F("hours") * F("hour_rate"))
            .aggregate(total=Sum("project_total"))
        )
        pdf.context = {
            "invoices": queryset,
            "seal": f"{STATIC_ROOT}/stationary/sign_md.png",
            "host": f"{protocal}://{request.get_host()}",
            "invoice_total": invoice_total.get("total"),
        }

        total_payment = invoice_total.get("total")

        body = f"Project Name:{project_name} \n Invoice Dates:{income_date_list_str} \n Total Payment:{total_payment}"
        if client.notes:
            body += f"\n Notes:{client.notes}"

        email = EmailMultiAlternatives(
            subject=f"Mediusware Invoice - {project_name} - {id_str}",
        )
        body = (body,)
        email.attach_file(pdf.create())
        email.to = [client.email]
        email.from_email = "coredeveloper.2013@gmail.com"
        email.cc = (client.cc_email.split(",") if client.cc_email else [],)
        email.send()
