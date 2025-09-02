from django.contrib import admin, messages
from django.utils.html import format_html

from inventory_management.forms import (
    InventoryItemForm,
    InventoryTransactionForm,
)
from inventory_management.models import (
    InventoryItem,
    InventoryItemHead,
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
