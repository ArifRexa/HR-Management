import datetime
import mimetypes
from urllib.parse import urlparse

import pandas as pd
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.db.models import F, Prefetch, Sum
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from weasyprint import CSS, HTML, default_url_fetcher

from account.models import (
    EmployeeSalary,
    ExpanseAttachment,
    Expense,
    ExpenseCategory,
    ExpenseGroup,
    TDSChallan,
)
from config.admin.utils import simple_request_filter
from employee.admin.employee._forms import DailyExpenseFilterForm
from employee.models import Employee


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "account_code",
        "get_vds_rate",
        "get_tds_rate",
        "note",
    )
    search_fields = ["title"]
    ordering = ["account_code"]

    @admin.display(description="VDS Rate (%)", ordering="vds_rate")
    def get_vds_rate(self, obj):
        return obj.vds_rate

    @admin.display(description="TDS Rate (%)", ordering="tds_rate")
    def get_tds_rate(self, obj):
        return obj.tds_rate

    def has_module_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "note")
    search_fields = ["title"]

    def has_module_permission(self, request):
        return False


class ExpanseAttachmentInline(admin.TabularInline):
    model = ExpanseAttachment
    extra = 1


class ActiveCreatedByFilter(admin.SimpleListFilter):
    title = "Created By"
    parameter_name = "created_by__employee__id__exact"

    def lookups(self, request, model_admin):
        clients = Employee.objects.filter(
            active=True, user__account_expense_related__isnull=False
        ).distinct()
        return tuple((client.pk, client.full_name) for client in list(clients))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created_by__employee__id__exact=self.value())
        return queryset


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "expanse_group",
        "expense_category",
        "get_amount",
        "note",
        "get_attachments",
        "get_approved",
        "get_authorized",
        "get_add_to_balance_sheet",
        "get_created_by",
    )
    date_hierarchy = "date"
    list_filter = [
        "is_authorized",
        "is_approved",
        ActiveCreatedByFilter,
        "expanse_group",
        "expense_category",
        "date",
    ]
    change_list_template = "admin/expense/list.html"
    inlines = [ExpanseAttachmentInline]
    search_fields = ["note"]
    actions = (
        "print_voucher",
        "print_voucher_attachment",
        "approve_expense",
        "add_to_balance_sheet",
        "remove_from_balance_sheet",
        "change_authorized_status",
    )
    autocomplete_fields = ("expanse_group", "expense_category")
    list_select_related = ("expanse_group", "expense_category", "created_by")
    list_per_page = 20

    # ✅ OPTIMIZATION 1: Centralized data fetching
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related(
            "expanse_group", "expense_category", "created_by"
        ).prefetch_related(
            Prefetch(
                "expanseattachment_set",
                queryset=ExpanseAttachment.objects.all(),
                to_attr="expense_attachment",
            )
        )

        if not request.user.has_perm(
            "account.can_approve_expense"
        ) and not request.user.has_perm("account.can_view_all_expenses"):
            return qs.filter(created_by__id=request.user.id)

        return qs

    # ✅ OPTIMIZATION 2: Efficient amount display
    @admin.display(description="Amount", ordering="amount")
    def get_amount(self, obj):
        # Assumes you want to format it as a currency. Much faster than template rendering.
        return f"{obj.amount:,.2f}"

    @admin.display(description="Checked", ordering="is_approved")
    def get_approved(self, obj):
        if obj.is_approved:
            return "✅"
        return "❌"

    @admin.display(description="Authorized", ordering="is_authorized")
    def get_authorized(self, obj):
        if obj.is_authorized:
            return "✅"
        return "❌"

    @admin.display(description="BS", ordering="add_to_balance_sheet")
    def get_add_to_balance_sheet(self, obj):
        if obj.add_to_balance_sheet:
            return "✅"
        return "❌"

    @admin.display(
        description="Created By", ordering="created_by__employee__full_name"
    )
    def get_created_by(self, obj):
        if obj.created_by:
            return obj.created_by.employee.full_name
        return "Unknown"

    # This method is now efficient because of get_queryset's prefetch_related
    @admin.display(
        description="Attachments", ordering="expanseattachment__count"
    )
    def get_attachments(self, obj):
        attachments = getattr(obj, "expense_attachment", None)
        if not attachments:
            return "-"
        url = reverse("account:expense_attachment", kwargs={"id": obj.id})
        html = f'<a href="{url}" target="_blank">📄</a>'

        return format_html(html)

    # ✅ OPTIMIZATION 3: Efficient voucher data mapping
    def _get_mapped_expense_data(self, queryset):
        user_ids = queryset.values_list("created_by", flat=True).distinct()
        users = User.objects.in_bulk(user_ids)

        mapped_data = []
        for expense_info in queryset.values("date", "created_by").distinct():
            context = dict(
                created_at=expense_info["date"],
                created_by=users.get(expense_info["created_by"]),
                data=queryset.filter(
                    date=expense_info["date"],
                    created_by=expense_info["created_by"],
                ),
            )
            mapped_data.append(context)
        return mapped_data

    # ... (the rest of your methods like get_actions, save_model, etc., remain the same)
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and not request.user.has_perm(
            "account.can_add_balance_sheet"
        ):
            actions.pop("add_to_balance_sheet")
            actions.pop("remove_from_balance_sheet")
        return actions

    @admin.action()
    def change_authorized_status(self, request, queryset):
        total = queryset.count()
        toggled_to_true = 0
        toggled_to_false = 0

        for obj in queryset:
            obj.is_authorized = not obj.is_authorized
            obj.save(update_fields=["is_authorized"])
            if obj.is_authorized:
                toggled_to_true += 1
            else:
                toggled_to_false += 1

        self.message_user(
            request,
            f"Toggled {total} items: {toggled_to_true} set to True, {toggled_to_false} set to False.",
        )

    def lookup_allowed(self, lookup, value):
        if lookup in ["created_by__employee__id__exact"]:
            return True
        return super().lookup_allowed(lookup, value)

    def get_readonly_fields(self, request, obj):
        rfs = super().get_readonly_fields(request, obj)
        rfs += ("approved_by",)
        if not request.user.is_superuser and not request.user.has_perm(
            "account.can_approve_expense"
        ):
            rfs += ("is_approved",)
        return rfs

    def has_change_permission(self, request, obj=None):
        perm = super().has_change_permission(request, obj)
        if perm and obj:
            if (
                not request.user.is_superuser
                and not request.user.has_perm("account.can_approve_expense")
                and obj.is_approved
            ):
                perm = False
        return perm

    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        if not request.user.is_superuser:
            qs.filter(created_by__id=request.user.id)
        return qs.aggregate(total=Sum("amount"))["total"]

    def changelist_view(self, request, extra_context=None):
        filter_form = DailyExpenseFilterForm(
            initial={
                "date__gte": request.GET.get(
                    "date__gte",
                    timezone.now().date() - datetime.timedelta(days=7),
                ),
                "date__lte": request.GET.get(
                    "date__lte", timezone.now().date()
                ),
            }
        )
        if request.GET:
            total = self.get_total_hour(request)
        else:
            total = None
        my_context = {"total": total, "filter_form": filter_form}
        return super().changelist_view(request, extra_context=my_context)

    @admin.action()
    def add_to_balance_sheet(self, request, queryset):
        queryset.update(add_to_balance_sheet=True)

    @admin.action()
    def remove_from_balance_sheet(self, request, queryset):
        queryset.update(add_to_balance_sheet=False)

    # @admin.action()
    # def print_voucher(self, request, queryset):
    #     pdf = PDF()
    #     pdf.context = dict(
    #         expense_groups=self._get_mapped_expense_data(queryset=queryset)
    #     )
    #     pdf.template_path = "voucher/expense_voucher.html"
    #     return pdf.render_to_pdf(download=False)

    @admin.action(description="Print Voucher")
    def print_voucher(self, request, queryset):
        monthly_journal = queryset.first()
        expense = queryset.values(
            "date", "expanse_group__title", "expense_category__title", "amount"
        )

        df = pd.DataFrame(list(expense))
        df.rename(
            columns={
                "date": "Date",
                "expanse_group__title": "Expense Group",
                "expense_category__title": "Expense Category",
                "amount": "Amount",
            },
            inplace=True,
        )
        df.loc["Total"] = df.sum(numeric_only=True, axis=0)
        df = df.fillna("")
        df.at["Total", "Expense Category"] = "Total"
        template = get_template("pdf/monthly_expense.html")
        context = {
            "table": df.to_html(index=False),
            "month": monthly_journal.date.strftime("%B"),
            "year": monthly_journal.date.strftime("%Y"),
        }
        html_content = template.render(context)
        month = monthly_journal.date.strftime("%B")
        year = monthly_journal.date.strftime("%Y")
        file_name_date = f"{month}/{year}"
        file_name = f"{file_name_date}_ME.pdf"

        # Generate PDF
        html = HTML(string=html_content)
        pdf_file = html.write_pdf()
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'

        return response

    @admin.action(description="Print Voucher (Attachment)")
    def print_voucher_attachment(self, request, queryset):
        monthly_journal = queryset.first()
        expense_paths = queryset.annotate(
            file=F("expanseattachment__attachment")
        ).values_list("file", flat=True)

        absolute_urls = []
        for relpath in expense_paths:
            if relpath:
                rel = (
                    relpath
                    if relpath.startswith("/")
                    else settings.MEDIA_URL + relpath
                )
                absolute_urls.append(request.build_absolute_uri(rel))

        context = {
            "expenses": absolute_urls,
            "month": monthly_journal.date.strftime("%B"),
            "year": monthly_journal.date.strftime("%Y"),
        }

        html_str = render_to_string(
            "pdf/monthly_expense_attachment.html", context
        )

        def custom_fetcher(url, *args, **kwargs):
            parsed = urlparse(url)
            if parsed.path.startswith(settings.MEDIA_URL):
                path = parsed.path.replace(
                    settings.MEDIA_URL, settings.MEDIA_ROOT + "/", 1
                )
                mime, enc = mimetypes.guess_type(path)
                return {
                    "file_obj": open(path, "rb"),
                    "mime_type": mime,
                    "encoding": enc,
                    "filename": path.split("/")[-1],
                }
            return default_url_fetcher(url, *args, **kwargs)

        html = HTML(
            string=html_str,
            base_url=request.build_absolute_uri("/"),
            url_fetcher=custom_fetcher,
        )
        css = CSS(string="@page { size: A4; margin: 1cm }")
        pdf_bytes = html.write_pdf(stylesheets=[css])
        month = monthly_journal.date.strftime("%B")
        year = monthly_journal.date.strftime("%Y")
        file_name = f"{month}/{year}"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        # file_name = f"{monthly_journal.date.strftime("%B")}_{monthly_journal.date.strftime("%Y")}"
        response["Content-Disposition"] = (
            f'attachment; filename="{file_name}_MA.pdf"'
        )
        return response

    @admin.action()
    def approve_expense(self, request, queryset):
        if request.user.is_superuser or request.user.has_perm(
            "account.can_approve_expense"
        ):
            queryset.update(is_approved=True, approved_by=request.user)

            messages.success(request, "Updated Successfully")
        else:
            messages.error(request, "You don't have enough permission")

    def get_form(self, request, obj, **kwargs):
        if not request.user.has_perm("account.can_approve_expense"):
            self.exclude = ["is_approved"]
        return super(ExpenseAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change) -> None:
        if obj.is_approved:
            obj.approved_by = request.user
        else:
            obj.approved_by = None
        return super().save_model(request, obj, form, change)


@admin.register(TDSChallan)
class TDSChallanAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "tds_month",
        "tds_type",
        "challan_no",
        "amount",
        "get_employee",
    )
    list_filter = ("tds_type", "tds_month", "employee")
    autocomplete_fields = ("employee",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("employee")

    @admin.display(description="Employee", ordering="employee__full_name")
    def get_employee(self, obj):
        if obj.tds_type == "individual":
            return obj.employee.first().full_name
        return ""

    def save_model(self, request, obj, form, change):
        tax_applied_employee_ids = EmployeeSalary.objects.filter(
            created_at__month=form.cleaned_data["tds_month"],
            created_at__year=form.cleaned_data["date"].year,
            loan_emi__lt=0,
        ).values_list("employee__id", flat=True)
        employee = Employee.objects.filter(id__in=tax_applied_employee_ids)

        form.cleaned_data["employee"] = employee
        return super().save_model(request, obj, form, change)
