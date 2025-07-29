import datetime
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import format_html

from account.models import Expense, ExpenseCategory, ExpanseAttachment, ExpenseGroup
from config.admin.utils import simple_request_filter
from config.utils.pdf import PDF
from employee.admin.employee._forms import DailyExpenseFilterForm
from employee.models import Employee

from django.contrib import messages


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "account_code", "note")
    search_fields = ["title"]
    ordering = ["account_code"]

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

# admin.py

from django.db.models import Prefetch, Sum
from django.utils.html import format_html


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "expanse_group",
        "expense_category",
        "get_amount",
        "note",
        "get_attachments",
        "created_by",
        "is_approved",
    )
    date_hierarchy = "date"
    list_filter = [
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
        "approve_expense",
        "add_to_balance_sheet",
        "remove_from_balance_sheet",
    )
    autocomplete_fields = ("expanse_group", "expense_category")
    list_select_related = ("expanse_group", "expense_category", "created_by")
    list_per_page = 20

    
    
    # ✅ OPTIMIZATION 1: Centralized data fetching
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("expanse_group", "expense_category", "created_by").prefetch_related("expanseattachment_set")
        
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

    # This method is now efficient because of get_queryset's prefetch_related
    @admin.display(description="Attachments", ordering="expanseattachment__count")
    def get_attachments(self, obj):
        # .all() here uses the prefetched cache, so no new DB query is made
        attachments = obj.expanseattachment_set.all()
        if not attachments:
            return "-"
        html = "".join(
            f'<a href="{attachment.attachment.url}" target="_blank">📄</a>'
            for attachment in attachments
        )
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
                    date=expense_info["date"], created_by=expense_info["created_by"]
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
                    "date__gte", timezone.now().date() - datetime.timedelta(days=7)
                ),
                "date__lte": request.GET.get("date__lte", timezone.now().date()),
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
    def print_voucher(self, request, queryset):
        pdf = PDF()
        pdf.context = dict(
            expense_groups=self._get_mapped_expense_data(queryset=queryset)
        )
        pdf.template_path = "voucher/expense_voucher.html"
        return pdf.render_to_pdf(download=False)

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