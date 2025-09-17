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
        # if obj.transaction_type == "i" and obj.status == "pending":  # IN
        #     item = InventoryItem.objects.get(id=obj.inventory_item.id)
        #     item.quantity = item.quantity - obj.quantity
        #     item.save()
        # elif obj.transaction_type == "o" and obj.status == "pending":  # OUT
        #     item = InventoryItem.objects.get(id=obj.inventory_item.id)
        #     item.quantity = item.quantity + obj.quantity
        #     item.save()
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

from dateutil.relativedelta import relativedelta
from django.utils import timezone


# Helper function to get start/end dates for n months ago
def get_start_end_dates(n_months_ago):
    today = timezone.now().date()
    target_month = today - relativedelta(months=n_months_ago)
    start_date = target_month.replace(day=1)
    end_date = target_month.replace(
        day=calendar.monthrange(target_month.year, target_month.month)[1]
    )
    return start_date, end_date


@admin.register(InventorySummary)
class InventorySummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/inventory/inventory_summary.html"
    sortable_fields = {
        "0": "inventory_item__name",
        "1": "inventory_item__quantity",
        "2": "current_total_out",
        "3": "one_month_ago_total_out",
        "4": "two_months_ago_total_out",
        "5": "three_months_ago_total_out",
    }

    def _build_queryset(self, request):
        # Get start/end dates for the last 4 months
        current_month = get_start_end_dates(0)
        one_month_ago = get_start_end_dates(1)
        two_months_ago = get_start_end_dates(2)
        three_months_ago = get_start_end_dates(3)

        # Calculate overall date range
        today = timezone.now().date()
        start_date_overall = today - relativedelta(months=3)
        start_date_overall = start_date_overall.replace(day=1)
        end_date_overall = today.replace(
            day=calendar.monthrange(today.year, today.month)[1]
        )

        qs = super().get_queryset(request)
        return (
            qs.filter(
                transaction_type="o",
                status="approved",
                transaction_date__lte=end_date_overall,
                transaction_date__gte=start_date_overall,
            )
            .values("inventory_item")
            .annotate(
                current_total_out=Sum(
                    "quantity",
                    filter=Q(
                        transaction_date__gte=current_month[0],
                        transaction_date__lte=current_month[1],
                    ),
                ),
                one_month_ago_total_out=Sum(
                    "quantity",
                    filter=Q(
                        transaction_date__gte=one_month_ago[0],
                        transaction_date__lte=one_month_ago[1],
                    ),
                ),
                two_months_ago_total_out=Sum(
                    "quantity",
                    filter=Q(
                        transaction_date__gte=two_months_ago[0],
                        transaction_date__lte=two_months_ago[1],
                    ),
                ),
                three_months_ago_total_out=Sum(
                    "quantity",
                    filter=Q(
                        transaction_date__gte=three_months_ago[0],
                        transaction_date__lte=three_months_ago[1],
                    ),
                ),
            )
            .values(
                "inventory_item__name",
                "current_total_out",
                "inventory_item__quantity",
                "one_month_ago_total_out",
                "two_months_ago_total_out",
                "three_months_ago_total_out",
            )
        )

    def get_sort_keys(self, request):
        o_param: str = request.GET.get("o", "")
        if o_param:
            if o_param.startswith("-"):
                sortable_field_key = o_param[1:]
                field = f"-{self.sortable_fields[sortable_field_key]}"
                return field, o_param
            sortable_field_key = o_param
            field = f"{self.sortable_fields[sortable_field_key]}"
            return field, o_param
        return "", ""

    def get_queryset(self, request):
        qs = self._build_queryset(request)
        sort_keys, _ = self.get_sort_keys(request)
        if sort_keys:
            qs = qs.order_by(sort_keys)
        return qs

    def changelist_view(self, request, extra_context=None):
        # Generate month names for headers
        today = timezone.now().date()
        month_names = ["Inventory Item", "Current Stock"]
        for i in range(4):
            month_date = today - relativedelta(months=i)
            month_names.append(month_date.strftime("%b %Y"))
        sort_keys, param = self.get_sort_keys(request)
        query_param = None
        for i, val in enumerate(month_names, start=1):
            if param and param.startswith("-"):
                if str(i) == param[1:]:
                    query_param = param[1:]
                    break
            else:
                query_param = f"-{param}"
                break

        extra_context = extra_context or {}

        extra_context.update(
            {
                "month_headers": month_names,
                "qs": self.get_queryset(request),
                "query_param": query_param,
            }
        )

        return super().changelist_view(request, extra_context)
