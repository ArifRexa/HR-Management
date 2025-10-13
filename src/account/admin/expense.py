import datetime
import mimetypes
import os
from urllib.parse import urlparse

from django.shortcuts import get_object_or_404
import pandas as pd
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Prefetch, Q, Sum
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
from inventory_management.models import InventoryTransaction
from settings.models import FinancialYear


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
        return False

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


class InventoryIdLinkWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        # Convert stored value to list of IDs
        ids = value.split(",") if value else []
        print("IDs:", ids)
        links = []

        for id_val in ids:
            try:
                # Fetch the actual object to build the link
                obj = InventoryTransaction.objects.get(
                    verification_code=id_val.strip()
                )
                link = f'<a href="/admin/inventory_management/inventorytransaction/{obj.pk}/change/" target="_blank">{id_val}</a>'
                links.append(link)
            except InventoryTransaction.DoesNotExist:
                links.append(f"{id_val} (invalid)")

        # Combine links into a single string
        links_html = ", ".join(links)
        print(links_html)

        # Render the base input field
        input_html = super().render(name, value, attrs, renderer)

        # Append links below the input field
        return f"""
            {input_html}
            <div class="inventory-links">
                {links_html}
            </div>
        """


class ExpenseAttachmentForm(forms.ModelForm):
    inventory_ids = forms.CharField(max_length=255, required=False, widget=InventoryIdLinkWidget())

    class Meta:
        model = ExpanseAttachment
        fields = ("note", "amount", "attachment", "inventory_ids")
        widgets = {
            "attachment": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "note": forms.Textarea(attrs={"rows": 3, "cols": 50}),
            # "inventory_ids": InventoryIdLinkWidget(),
        }

    def clean_inventory_ids(self):
        inventory_ids = self.cleaned_data.get("inventory_ids", None)

        if inventory_ids:
            id_list = [id.strip() for id in inventory_ids.split(",")]

            inventories = InventoryTransaction.objects.filter(
                verification_code__in=id_list, transaction_type="i"
            )
            if len(id_list) > inventories.count():
                raise ValidationError(
                    "One of the Inventory Id Not exist in Inventory Item Table"
                )
            self.cleaned_data["inventory"] = inventories.values_list(
                "id", flat=True
            )
        return inventory_ids

    def save(self, commit=True, **kwargs):
        # Save the base object first
        instance = super().save(commit=False, **kwargs)
        instance.save()
        # Get validated inventory objects from cleaned data
        inventory_objects = self.cleaned_data.get("inventory", [])

        # Set the Many-to-Many relationship
        instance.inventory.set(inventory_objects)

        if commit:
            instance.save()

        return instance

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")

        if attachment:
            # Basic image validation (handled by ImageField)
            # Add custom format restrictions if needed
            allowed_formats = ["jpg", "jpeg", "png", "gif"]
            ext = os.path.splitext(attachment.name)[1][1:].lower()
            if ext not in allowed_formats:
                raise ValidationError(
                    f"Only {', '.join(allowed_formats)} files are allowed"
                )

        return attachment


class ExpanseAttachmentInline(admin.TabularInline):
    model = ExpanseAttachment
    extra = 1
    form = ExpenseAttachmentForm

    # def get_readonly_fields(self, request, obj=None):
    #     d = request.user.has_perm("account.can_update_expense_attachment")
    #     f = super().get_readonly_fields(request, obj)
    #     if obj.is_approved and not request.user.has_perm(
    #         "account.can_update_expense_attachment"
    #     ):
    #         return ["note", "amount", "attachment", "inventory_ids"]
    #     return f


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


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        is_approved = cleaned_data.get("is_approved")
        obj = self.instance
        attachments = obj.expanseattachment_set.all()
        
        # for attachment in obj.expanseattachment_set.all():
        #     group_title = obj.expanse_group.title.lower()
        #     if not attachment.inventory_ids and group_title in [
        #         "office expense",
        #         "office supplies & stationery",
        #         "entertainment",
        #     ]:
        #         raise ValidationError(f"you must give inventory ids for {group_title} group")
        
        # Only validate if the object is approved
        if is_approved:
            # Current model instance (unsaved/new)

            # Get inventory IDs from related ExpanseAttachments
            inventory_ids = []
            for attachment in attachments:
                # Handle different data types (list/JSON/string)
                if isinstance(attachment.inventory_ids, str):
                    inventory_ids.extend(
                        [
                            id.strip()
                            for id in attachment.inventory_ids.split(",")
                        ]
                    )
                else:
                    inventory_ids.extend(attachment.inventory_ids)

            # Check for pending inventory transactions
            if (
                inventory_ids
                and InventoryTransaction.objects.filter(
                    verification_code__in=inventory_ids, status="pending"
                ).exists()
            ):
                raise ValidationError(
                    {"is_approved": "First accept inventory transactions."}
                )

        return cleaned_data
    # def clean(self):
    #     cleaned_data = super().clean()
    #     is_approved = cleaned_data.get("is_approved")
    #     obj = self.instance
        
    #     # Check if expanse_group is set before accessing its title
    #     if not obj.expanse_group:
    #         raise ValidationError({"expanse_group": "Expense group must be set."})
        
    #     group_title = obj.expanse_group.title.lower()
        
    #     attachments = obj.expanseattachment_set.all()
    #     for attachment in attachments:
    #         # First check if inventory_ids exists and is not empty
    #         if not attachment.inventory_ids and group_title in [
    #             "office expense",
    #             "office supplies & stationery",
    #             "entertainment",
    #         ]:
    #             raise ValidationError(f"you must give inventory ids for {group_title} group")
        
    #     # Only validate if the object is approved
    #     if is_approved:
    #         # Get inventory IDs from related ExpanseAttachments
    #         inventory_ids = []
    #         for attachment in attachments:
    #             # Skip if inventory_ids is None
    #             if attachment.inventory_ids is None:
    #                 continue
                    
    #             # Handle different data types (list/JSON/string)
    #             if isinstance(attachment.inventory_ids, str):
    #                 # Split the string and ensure we don't have empty strings
    #                 ids = [id.strip() for id in attachment.inventory_ids.split(",") if id.strip()]
    #                 inventory_ids.extend(ids)
    #             elif isinstance(attachment.inventory_ids, (list, tuple)):
    #                 # Only extend if it's a list or tuple
    #                 inventory_ids.extend(attachment.inventory_ids)
            
    #         # Check for pending inventory transactions
    #         if (
    #             inventory_ids
    #             and InventoryTransaction.objects.filter(
    #                 verification_code__in=inventory_ids, status="pending"
    #             ).exists()
    #         ):
    #             raise ValidationError(
    #                 {"is_approved": "First accept inventory transactions."}
    #             )
    #     return cleaned_data


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "expanse_group",
        "expense_category",
        "get_amount",
        "get_notes",
        "get_attachments",
        "get_add_to_balance_sheet",
        "get_approved",
        "get_authorized",
        "get_created_by",
    )
    date_hierarchy = "date"
    list_filter = [
        "is_authorized",
        "is_approved",
        "add_to_balance_sheet",
        ActiveCreatedByFilter,
        "expanse_group",
        "expense_category",
        "date",
    ]
    change_list_template = "admin/expense/list.html"
    inlines = [ExpanseAttachmentInline]
    search_fields = ["note", "id"]
    actions = (
        "print_voucher",
        "print_voucher_attachment",
        "approve_expense",
        # "add_to_balance_sheet",
        # "remove_from_balance_sheet",
        "change_reviewer_status",
        "change_authorized_status",
    )
    autocomplete_fields = ("expanse_group", "expense_category")
    list_select_related = ("expanse_group", "expense_category", "created_by")
    list_per_page = 20
    readonly_fields = ("amount",)
    form = ExpenseForm

    class Media:
        css = {"all": ("css/list.css", "css/daily-update.css")}
        js = ("expense_total_amount.js",)

    # @admin.display(description="Notes")
    # def get_notes(self, obj):
    #     html_template = get_template("admin/expense/list/col_note.html")

    #     html_content = html_template.render(
    #         {
    #             "obj": obj,
    #         }
    #     )

    #     try:
    #         data = format_html(html_content)
    #     except:
    #         data = "-"

    #     return data
    @admin.display(description="Notes")
    def get_notes(self, obj):
        # Determine the note to display
        display_note = obj.note
        if not display_note:
            for attachment in obj.expense_attachment:
                if attachment.note:
                    display_note = attachment.note
                    break
        if not display_note:
            display_note = "-"

        # Pass it to template
        html_template = get_template("admin/expense/list/col_note.html")
        html_content = html_template.render({
            "obj": obj,
            "display_note": display_note,  # Add this
        })

        try:
            return format_html(html_content)
        except Exception:
            return "-"

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

    @admin.display(description="Reviewer", ordering="add_to_balance_sheet")
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
    # @admin.display(
    #     description="Attachments", ordering="expanseattachment__count"
    # )
    # def get_attachments(self, obj):
    #     attachments = getattr(obj, "expense_attachment", None)
    #     if not attachments:
    #         return "-"
    #     url = reverse("account:expense_attachment", kwargs={"id": obj.id})
    #     html = f'<a href="{url}" target="_blank">📄</a>'

    #     return format_html(html)
    @admin.display(description="Attachments", ordering="expanseattachment__count")
    def get_attachments(self, obj):
        attachments = getattr(obj, "expense_attachment", [])
        if not attachments:
            return "-"

        # Base URL for the attachment list view
        url = reverse("account:expense_attachment", kwargs={"id": obj.id})
        lines = [f'<a href="{url}" target="_blank">📄</a> <br>']  # Keep the file icon

        # Process inventory IDs from each attachment
        for attachment in attachments:
            inv_ids_str = attachment.inventory_ids
            if not inv_ids_str:
                continue

            # Split and clean IDs
            inv_ids = [id.strip() for id in inv_ids_str.split(",") if id.strip()]
            for inv_id in inv_ids:
                try:
                    # Try to find the InventoryTransaction by verification_code
                    inv_transaction = InventoryTransaction.objects.get(
                        verification_code=inv_id, transaction_type="i"
                    )
                    link = (
                        f'<a href="/admin/inventory_management/inventorytransaction/'
                        f'{inv_transaction.pk}/change/" '
                        f'target="_blank" style="font-size:11px;">{inv_id}</a>'
                    )
                except InventoryTransaction.DoesNotExist:
                    link = f'<span style="font-size:11px; color:#999;">{inv_id} (invalid)</span>'
                lines.append(link)

        return format_html("<br>".join(lines))

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
        if not request.user.is_superuser:
            actions.pop("change_authorized_status")
        # if not request.user.is_superuser and not request.user.has_perm(
        #     "account.can_add_balance_sheet"
        # ):
        #     actions.pop("add_to_balance_sheet")
        #     actions.pop("remove_from_balance_sheet")
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
                and not request.user.has_perm(
                    "account.can_update_expense_attachment"
                )
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

    @admin.action()
    def change_reviewer_status(self, request, queryset):
        if queryset.filter(add_to_balance_sheet=True):
            queryset.update(add_to_balance_sheet=False)
        else:
            queryset.update(add_to_balance_sheet=True)

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
        if self.exclude is None:
            self.exclude = []
        if not request.user.is_superuser and not request.user.has_perm(
            "account.can_approve_expense"
        ):
            self.exclude += ["is_approved"]
        if not request.user.is_superuser:
            self.exclude += ["add_to_balance_sheet", "is_authorized"]
        if not request.user.is_superuser and not request.user.has_perm(
            "account.can_see_note_field"
        ):
            self.exclude += ["note"]
        return super(ExpenseAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change) -> None:
        if obj.is_approved:
            obj.approved_by = request.user
        else:
            obj.approved_by = None
        return super().save_model(request, obj, form, change)


from django.contrib import admin


class TDSEmployeeFilter(admin.SimpleListFilter):
    title = "Employee"
    parameter_name = "employee"

    # ------------------------------------------------------------------
    # 1. Build the list of choices (unique, already sorted by DB)
    # ------------------------------------------------------------------
    def lookups(self, request, model_admin):
        individual_qs = TDSChallan.objects.filter(
            individual_employee__isnull=False
        ).values_list(
            "individual_employee_id", "individual_employee__full_name"
        )

        group_qs = TDSChallan.objects.values_list(
            "employee__id", "employee__full_name"
        )

        choices = individual_qs.union(group_qs, all=False)
        return tuple(choices)

    def queryset(self, request, queryset):
        emp_id = self.value()
        if not emp_id:
            return queryset

        # single WHERE clause with OR
        return queryset.filter(
            Q(individual_employee_id=emp_id) | Q(employee__id=emp_id)
        )


class TDSChallanForm(forms.ModelForm):
    class Meta:
        model = TDSChallan
        exclude = ("individual_employee",)

    def clean(self):
        cleaned = super().clean()
        tds_type = cleaned.get("tds_type")
        employees = cleaned.get("employee")

        if tds_type == "individual":
            if not employees:
                raise ValidationError(
                    {
                        "employee": "Individual TDS type must have an employee selected."
                    }
                )
        elif tds_type == "group":
            if not employees:
                # Find eligible employees based on logic
                tax_applied_ids = EmployeeSalary.objects.filter(
                    created_at__month=cleaned.get("tds_month"),
                    created_at__year=cleaned.get("date").year,
                    loan_emi__lt=0,
                ).values_list("employee__id", flat=True)
                if not tax_applied_ids:
                    raise ValidationError(
                        "No eligible employees found for the selected month and year."
                    )
                cleaned["employee"] = Employee.objects.filter(
                    id__in=tax_applied_ids
                )

        return cleaned


@admin.register(TDSChallan)
class TDSChallanAdmin(admin.ModelAdmin):
    list_display = (
        "tds_year",
        "tds_month",
        "tds_type",
        "date",
        "challan_no",
        "amount",
        "get_employee",
    )
    exclude = ("individual_employee", "tds_order")
    form = TDSChallanForm
    list_filter = ("tds_type", "tds_year", "tds_month", TDSEmployeeFilter)
    autocomplete_fields = ("employee",)
    actions = ("add_individual_employee", "set_tds_year", "ordered_tds_challan")
    search_fields = (
        "challan_no",
        "employee__full_name",
        "individual_employee__full_name",
    )
    date_hierarchy = "date"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("employee")
            .select_related("individual_employee")
        )

    @admin.display(
        description="Employee", ordering="individual_employee__full_name"
    )
    def get_employee(self, obj):
        return obj.individual_employee

    @admin.action(description="Add Individual Employee")
    def add_individual_employee(self, request, queryset):
        # 1. Grab only the records that still need the fix.
        with transaction.atomic():
            to_fix = (
                queryset.select_for_update(skip_locked=True)
                .filter(
                    tds_type="individual",
                    individual_employee__isnull=True,
                    employee__isnull=False,
                )
                .distinct()
            )

            if not to_fix:
                messages.warning(
                    request, "No valid TDS challans need updating."
                )
                return

            # 2. Prefetch the employee list so we don't hit the DB in the loop.
            to_fix = to_fix.prefetch_related("employee")

            updated = 0
            updates = []

            for challan in to_fix:
                first_emp = challan.employee.first()
                if first_emp:
                    challan.individual_employee = first_emp
                    updates.append(challan)
                    updated += 1

            # 3. One UPDATE statement for all rows.
            if updates:
                TDSChallan.objects.bulk_update(updates, ["individual_employee"])

        messages.success(
            request, f"Individual employee added to {updated} TDS challan(s)."
        )

    @admin.action(description="Ordered TDS challans")
    def ordered_tds_challan(self, request, queryset):
        import datetime

        updated = 0
        with transaction.atomic():
            for ch in queryset:
                if ch.tds_year and ch.tds_month:
                    fy_start_year = ch.tds_year.start_date.year
                    year = (
                        fy_start_year
                        if 7 <= ch.tds_month <= 12
                        else fy_start_year + 1
                    )
                    ch.tds_order = datetime.date(year, ch.tds_month, 1)
                    ch.save(update_fields=["tds_order"])
                    updated += 1

        self.message_user(
            request,
            f"{updated} TDS challan(s) now have a TDS-order date.",
            messages.SUCCESS,
        )

    @admin.action(description="Set TDS Year")
    def set_tds_year(self, request, queryset):
        active_year = FinancialYear.objects.filter(active=True).first()
        qs = queryset.filter(tds_year__isnull=True)
        if not active_year:
            self.message_user(
                request,
                "No active financial year found. Please set one in settings.",
                messages.ERROR,
            )

        else:
            updated = qs.update(tds_year=active_year)
            if updated:
                self.message_user(
                    request,
                    f"Set TDS Year to {active_year} for {updated} TDS challan(s).",
                    messages.SUCCESS,
                )
            else:
                self.message_user(
                    request, "No TDS challans needed updating.", messages.INFO
                )

    def save_model(self, request, obj, form, change):
        obj.individual_employee = None
        if form.cleaned_data["tds_type"] == "individual":
            obj.individual_employee = form.cleaned_data["employee"][0]
        return super().save_model(request, obj, form, change)
