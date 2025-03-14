from django.contrib import admin, messages
from django.db import models
from admin_confirm.admin import AdminConfirmMixin, confirm_action
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce
from django.forms import Textarea
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import get_template
import requests
from account.models import Income
from account.services.balance import BalanceSummery

import config.settings
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


class IncomeFilterBySendInvoiceEmail(admin.SimpleListFilter):
    title = "Send Email"
    parameter_name = "is_send_invoice_email"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(is_send_invoice_email=self.value())
        return queryset


@admin.register(Income)
class IncomeAdmin(AdminConfirmMixin, admin.ModelAdmin):
    list_display = (
        "project",
        "date",
        "hours",
        "hour_rate",
        # "convert_rate",
        "payment_details",
        "get_send_email_status",
        "status_col",
    )
    date_hierarchy = "date"
    exclude = ["is_send_clients", "loss_hours", "is_send_invoice_email", "payment", "convert_rate", "pdf_url"]
    # readonly_fields = ("payment",)
    list_filter = [
        "status",
        IncomeFilterBySendInvoiceEmail,
        "project",
        "project__client__payment_method",
        "project__client__invoice_type",
        ActiveClientFilter,
    ]
    actions = [
        "approve_selected",
        "pending_selected",
        "hold_selected",
        "print_income_invoices",
        "send_income_invoices_email",
    ]
    # list_editable = ('status',)
    formfield_overrides = {models.TextField: {"widget": Textarea(attrs={"rows": 2})}}
    autocomplete_fields = ["project"]

    change_list_template = "admin/income/list.html"

    list_per_page = 20

    @admin.display(description="Email")
    def get_send_email_status(self, obj):
        color = "red"
        if obj.is_send_invoice_email == "yes":
            color = "green"
        return format_html(
            f'<b style="color: {color}">{obj.get_is_send_invoice_email_display()}</b>'
        )

    def get_actions(self, request):
        action = super().get_actions(request)
        has_permission_view_status = request.user.is_superuser or request.user.has_perm(
            "account.can_view_income_status"
        )

        if not has_permission_view_status:
            action.pop("pending_selected")
            action.pop("approve_selected")
        return action

    def get_list_display(self, request):
        display = super().get_list_display(request)
        has_status_permission = request.user.is_superuser or request.user.has_perm(
            "account.can_view_income_status"
        )
        display = list(display)
        if not has_status_permission:
            display.remove("status_col")
        return display

    def get_list_filter(self, request):
        filters = super().get_list_filter(request)
        if not request.user.has_perm("project_management.view_client"):
            filters = [f for f in filters if f != "project__client__payment_method"]

        return filters
        # if not request.user.has_perm("project_management.view_client"):
        #     self.list_filter.remove("project__client__payment_method")
        #     return self.list_filter
        # return super().get_list_filter(request)

    @admin.action(description="Status")
    def status_col(self, obj):
        color = "red"
        if obj.status == "approved":
            color = "green"
        return format_html(f'<b style="color: {color}">{obj.get_status_display()}</b>')

    # @admin.display()
    # def payment_details(self, obj):
    #     return format_html(
    #         f"<b style='color: green; font-size: 16px'>$ {obj.payment / obj.convert_rate}</b> / "
    #         f"{obj.payment} TK"
    #     )

    @admin.display()
    def payment_details(self, obj):
        # Get the client's currency icon
        currency_icon = obj.project.client.currency.icon if obj.project.client.currency else '$'

        # print("**************************************************")
        # print(obj.project.client.currency)

        return format_html(
            f"<b style='color: green; font-size: 16px'>{currency_icon} {obj.payment / obj.convert_rate}</b> / "
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
        # if not request.user.is_superuser:
        #     filters["created_by__id__exact"] = request.user.employee.id
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
        queryset.update(status="approved", is_send_invoice_email="yes")
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
    def hold_selected(self, request, queryset):
        queryset.update(status="hold")
        self.message_user(request, f'Status has been updated to hold for {len(queryset)} items', messages.SUCCESS)


    @admin.action()
    def print_income_invoices(self, request, queryset):
        queryset = queryset.order_by("date")
        income_list = queryset.values_list("id", flat=True)
        id_str = "_".join(list(map(str, income_list)))
        project_name = queryset.first().project.title
        client = queryset.first().project.client
        pdf = PDF()
        pdf.file_name = f"Income Invoice-{project_name}-{id_str}"
        if not client.bill_from:
            pdf_template = "compliance/new_income_invoice.html"
        else:
            pdf_template = "compliance/invoice_without_watermark.html"
        pdf.template_path = pdf_template
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
            "currency_icon": client.currency.icon if client.currency else '$',
            "invoice_total": invoice_total.get("total"),
        }
        return pdf.render_to_pdf(download=True)

    # @admin.action()
    # def send_income_invoices_email(self, request, queryset):
    #     queryset = queryset.order_by("date")
    #     income_list = queryset.values_list("id", flat=True)
    #     income_date_list = queryset.values_list("date", flat=True)
    #     income_date_list_str = "|".join(list(map(str, income_date_list)))
    #     id_str = "|".join(list(map(str, income_list)))
    #     project_name = queryset.first().project.title
    #     client = queryset.first().project.client
    #     # project_name = "-".join(project_name.split(" "))
    #     pdf = PDF()
    #     pdf.file_name = f"Income-Invoice-{project_name}-{id_str}"
    #     pdf.template_path = "compliance/new_income_invoice.html"
    #     protocal = "https" if request.is_secure() else "http"
    #     invoice_total = (
    #         queryset.values("date", "hour_rate")
    #         .annotate(project_total=F("hours") * F("hour_rate"))
    #         .aggregate(total=Sum("project_total"))
    #     )
    #     pdf.context = {
    #         "invoices": queryset,
    #         "seal": f"{STATIC_ROOT}/stationary/sign_md.png",
    #         "host": f"{protocal}://{request.get_host()}",
    #         "invoice_total": invoice_total.get("total"),
    #     }

    #     total_payment = invoice_total.get("total")

    #     body = f"Project Name:{project_name} \n Invoice Dates:{income_date_list_str} \n Total Payment:{total_payment}"
    #     if client.notes:
    #         body += f"\n Notes:{client.notes}"

    #     email = EmailMultiAlternatives(
    #         subject=f"Mediusware Invoice - {project_name} - {id_str}",
    #     )
    #     body = (body,)
    #     email.attach_file(pdf.create())
    #     email.to = [client.email]
    #     email.from_email = "hr@mediusware.com"
    #     email.cc = [client.cc_email.split(",") if client.cc_email else []]
    #     email.send()

    @admin.action()
    def send_income_invoices_email(self, request, queryset):
        try:
            queryset = queryset.order_by("date")
            income_list = queryset.values_list("id", flat=True)
            id_str = "|".join(list(map(str, income_list)))
            project_name = queryset.first().project.title
            client = queryset.first().project.client
            project_name = "-".join(project_name.split(" "))
            pdf = PDF()
            pdf.file_name = f"Income-Invoice-{project_name}-{id_str}"
            if not client.bill_from:
                pdf_template = "compliance/new_income_invoice.html"
            else:
                pdf_template = "compliance/invoice_without_watermark.html"
            pdf.template_path = pdf_template
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
                "currency_icon": client.currency.icon if client.currency else '$',
                "invoice_total": invoice_total.get("total"),
            }

            total_payment = invoice_total.get("total")
            email_template = get_template("mail/income_invoice_mail.html")
            invoice_dates = ",".join(
                {
                    date.strftime("%b %-d")
                    for date in queryset.values_list("date", flat=True)
                }
            )
            html_content = email_template.render(
                {
                    "currency_icon": client.currency.icon if client.currency else '$',
                    "invoice_dates": invoice_dates,
                    "client_name": client.name,
                    "total_amount": total_payment,
                    "client_notes": client.notes if client.notes else "",
                }
            )

            # body = f"Project Name:{project_name} \n Invoice Dates:{income_date_list_str} \n Total Payment:{total_payment}"
            # if client.notes:
            #     body += f"\n Notes:{client.notes}"
            month = queryset.first().date.strftime("%B")
            invoice_number = f"INV-{queryset.first().id}"
            email = EmailMultiAlternatives(
                subject=f"Your Invoice from Mediusware [{month}/{invoice_number}] || Your Trusted B2B Outstaffing Partner"
            )
            pdf_url = pdf.create()
            if pdf_url and pdf_url.__contains__("http"):
                # Fetch the PDF content from the URL
                response = requests.get(pdf_url)

                print("file name:", pdf_url.split("/")[-1])
                email.attach(
                    pdf_url.split("/")[-1], response.content, "application/pdf"
                )
            else:
                email.attach_file(pdf_url)

            # body = (body,)
            # email.attach_file(pdf.create())
            client_cc_email = (
                client.invoice_cc_email.split(",") if client.invoice_cc_email else []
            )
            email.attach_alternative(html_content, "text/html")
            email.to = [client.email]
            email.from_email = "shahinur@mediusware.com"
            # email.cc = ["shahinur@mediusware.com", "badhan@mediusware.com", "tanvir@mediusware.com"]
            email.cc = ["invoice@mediusware.com"] + client_cc_email
            email.send()
            self.message_user(
                request,
                f"Email sent to {client.name} successfully",
                messages.SUCCESS,
            )
            queryset.update(is_send_invoice_email="yes")
        except Exception as e:
            print(e)
            self.message_user(request, "Something went wrong", messages.ERROR)
