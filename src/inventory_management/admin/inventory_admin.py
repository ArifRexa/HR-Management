from django.contrib import admin, messages
from django.db.models import Q, Sum
from django.utils.html import format_html

from inventory_management.forms import (
    InventoryItemForm,
    InventoryTransactionForm,
)
from inventory_management.models import (
    InventoryItem,
    InventoryItemHead,
    InventorySummary,
    InventoryTransaction,
    InventoryUnit,
)

# Register your models here.


@admin.register(InventoryItemHead)
class InventoryItemHeadAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("show_item_name", "show_quantity", "unit")
    readonly_fields = ["quantity"]
    search_fields = ("name",)
    form = InventoryItemForm
    # autocomplete_fields = ("head",)
    list_filter = ("unit",)

    @admin.display(description="head", ordering="head.title")
    def get_head(self, obj):
        return obj.head.title or "-"

    @admin.display(description="item name", ordering="name")
    def show_item_name(self, obj):
        string = f"<strong>{obj.name}</strong>"
        if obj.quantity <= obj.reorder_point:
            string = f'<strong style="color:red">{obj.name}</strong>'
        return format_html(string)

    @admin.display(description="quantity", ordering="quantity")
    def show_quantity(self, obj):
        string = f"<strong>{obj.quantity}</strong>"
        if obj.quantity <= obj.reorder_point:
            string = f'<strong style="color:red">{obj.quantity}</strong>'
        return format_html(string)


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_date",
        "inventory_item",
        "quantity",
        "transaction_type",
        "colored_status",
        "verification_code",
        "get_created_by",
    )
    list_filter = (
        "status",
        "inventory_item",
        "transaction_type",
    )
    search_fields = ("inventory_item",)
    exclude = ("updated_by", "verification_code")
    actions = ["mark_as_approved", "mark_as_pending"]
    date_hierarchy = "transaction_date"
    autocomplete_fields = ("inventory_item",)
    form = InventoryTransactionForm

    @admin.display(description="Created By")
    def get_created_by(self, obj):
        return (
            obj.created_by.employee.full_name
            if obj.created_by.employee
            else obj.created_by.username
        )

    @admin.display(description="status", ordering="status")
    def colored_status(self, obj):
        colors = {
            "pending": "#FF0000",  # Orange
            "approved": "#28a745",  # Green
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, "black"),
            obj.get_status_display(),
        )

    def save_model(self, request, obj, form, change):
        if obj.transaction_type == "i" and obj.status == "approved":  # IN
            item = InventoryItem.objects.get(id=obj.inventory_item.id)
            item.quantity = item.quantity + obj.quantity
            item.save()
        elif obj.transaction_type == "o" and obj.status == "approved":  # OUT
            item = InventoryItem.objects.get(id=obj.inventory_item.id)
            item.quantity = item.quantity - obj.quantity
            item.save()
        if obj.transaction_type == "i" and obj.status == "pending":  # IN
            item = InventoryItem.objects.get(id=obj.inventory_item.id)
            item.quantity = item.quantity - obj.quantity
            item.save()
        elif obj.transaction_type == "o" and obj.status == "pending":  # OUT
            item = InventoryItem.objects.get(id=obj.inventory_item.id)
            item.quantity = item.quantity + obj.quantity
            item.save()
        super().save_model(request, obj, form, change)

    @admin.action(description="Mark Selected Inventory as Approved")
    def mark_as_approved(self, request, queryset):
        for obj in queryset:
            if obj.transaction_type == "i":  # IN
                item = InventoryItem.objects.get(id=obj.inventory_item.id)
                item.quantity = item.quantity + obj.quantity
                item.save()
            elif obj.transaction_type == "o":  # OUT
                item = InventoryItem.objects.get(id=obj.inventory_item.id)
                item.quantity = item.quantity - obj.quantity
                item.save()
        queryset.update(status="approved")
        self.message_user(
            request,
            "Selected transactions approved successfully",
            messages.SUCCESS,
        )

    @admin.action(description="Mark Selected Inventory as Pending")
    def mark_as_pending(self, request, queryset):
        for obj in queryset:
            if obj.transaction_type == "i":  # IN
                item = InventoryItem.objects.get(id=obj.inventory_item.id)
                item.quantity = item.quantity - obj.quantity
                item.save()
            elif obj.transaction_type == "o":  # OUT
                item = InventoryItem.objects.get(id=obj.inventory_item.id)
                item.quantity = item.quantity + obj.quantity
                item.save()
        queryset.update(status="pending")
        self.message_user(
            request, "Selected inventory marked as pending", messages.SUCCESS
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and not request.user.has_perm(
            "inventory_management.can_change_inventory_status"
        ):
            actions.pop(
                "mark_as_approved", None
            )  # Remove the "Mark as Approved" action
            actions.pop(
                "mark_as_pending", None
            )  # Remove the "Mark as Pending" action
        return actions

    def get_fields(self, request, obj=...):
        fields = super().get_fields(request, obj)
        fields = list(fields)
        if not request.user.is_superuser and not request.user.has_perm(
            "inventory_management.can_change_inventory_status"
        ):
            fields.remove("status")

        return fields


admin.site.register(InventoryUnit)


import calendar
from datetime import datetime

from dateutil.relativedelta import relativedelta


def get_current_month_range(date):
    first_day = date.replace(day=1)
    last_day = date.replace(day=calendar.monthrange(date.year, date.month)[1])
    return first_day.date(), last_day.date()


def get_start_of_month_n_months_ago(n=0):
    today = datetime.today()
    if n == 0:
        return get_current_month_range(today)
    start_of_previous_month = today - relativedelta(months=n)
    return get_current_month_range(start_of_previous_month)


@admin.register(InventorySummary)
class InventorySummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/inventory/inventory_summary.html"
    date_hierarchy = "transaction_date"
    list_filter = ("inventory_item",)


    def changelist_view(self, request, extra_context=None):
        current_month = get_start_of_month_n_months_ago()
        before_1_month = get_start_of_month_n_months_ago(1)
        before_2_month = get_start_of_month_n_months_ago(2)
        today = datetime.today()
        start_data = today.replace(day=calendar.monthrange(today.year, today.month)[1]).date()
        before_2 = today - relativedelta(months=2)
        end_date = before_2.replace(
            day=1
        )
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        extra_context["qs"] = (
            qs.filter(
                transaction_type="o",
                status="approved",
                transaction_date__lte=start_data,
                transaction_date__gte=end_date,
            )
            .values("inventory_item")
            .annotate(
                current_total_out=Sum(
                    "quantity",
                    filter=(
                        Q(transaction_date__gte=current_month[0])
                        & Q(transaction_date__lte=current_month[1])
                    ),
                ),
                before_1_total_out=Sum(
                    "quantity",
                    filter=(
                        Q(transaction_date__gte=before_1_month[0])
                        & Q(transaction_date__lte=before_1_month[1])
                    ),
                ),
                before_2_total_out=Sum(
                    "quantity",
                    filter=(
                        Q(transaction_date__gte=before_2_month[0])
                        & Q(transaction_date__lte=before_2_month[1])
                    ),
                ),
            )
            .order_by("-current_total_out")
            .values(
                "inventory_item__name",
                "current_total_out",
                "inventory_item__quantity",
                "before_1_total_out",
                "before_2_total_out",
            )
        )
        return super().changelist_view(request, extra_context)
