from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from inventory_management.models import (
    InventoryItem,
    InventoryTransaction,
    InventoryUnit
)
from inventory_management.forms import InventoryTransactionForm, InventoryItemForm

# Register your models here.

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("show_item_name", "show_quantity","unit")
    readonly_fields = ["quantity"]
    search_fields = ("name",)
    form = InventoryItemForm

    @admin.display(description="item name", ordering="name")
    def show_item_name(self, obj):
        string = f'<strong>{obj.name}</strong>'
        if obj.quantity <= obj.reorder_point:
            string = f'<strong style="color:red">{obj.name}</strong>'
        return format_html(string)
    

    @admin.display(description="quantity", ordering="quantity")
    def show_quantity(self, obj):
        string = f'<strong>{obj.quantity}</strong>'
        if obj.quantity <= obj.reorder_point:
            string = f'<strong style="color:red">{obj.quantity}</strong>'
        return format_html(string)



@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_date","inventory_item", "quantity","transaction_type", "created_by")
    list_filter = ("inventory_item","transaction_type",)
    search_fields = ("inventory_item",)
    date_hierarchy = "transaction_date"
    autocomplete_fields = ("inventory_item",)
    form = InventoryTransactionForm
    
    def save_model(self, request, obj, form, change):
        if obj.transaction_type == "i": #IN
            item = InventoryItem.objects.get(id=obj.inventory_item.id)
            item.quantity = item.quantity+obj.quantity
            item.save()
        elif obj.transaction_type == "o": #OUT
            item = InventoryItem.objects.get(id=obj.inventory_item.id)
            item.quantity = item.quantity-obj.quantity
            item.save()
        super().save_model(request, obj, form, change)


admin.site.register(InventoryUnit)
