from django import forms

from inventory_management.models import (
    InventoryItem,
    InventoryTransaction,
    InventoryUnit,
)


class InventoryTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("transaction_type")
        quantity = cleaned_data.get("quantity")
        item = cleaned_data.get("inventory_item")

        if item is None:
            raise forms.ValidationError(
                {"inventory_item": "Please Select an Item."}
            )

        inventory_item = InventoryItem.objects.get(id=item.id)

        if inventory_item.quantity < quantity and transaction_type == "o":
            raise forms.ValidationError(
                {
                    "quantity": "Cannot use more items than available in inventory. First In this Item"
                }
            )

        if (
            not self.instance
            and InventoryTransaction.objects.filter(
                inventory_item=inventory_item,
                status="pending",
                transaction_type="o",
            ).exists()
        ):
            raise forms.ValidationError(
                {
                    "inventory_item": "There is already a pending transaction for this item."
                }
            )

        if quantity is None:
            raise forms.ValidationError({"quantity": "Quantity is required."})

        if quantity <= 0:
            raise forms.ValidationError(
                {"quantity": "Quantity must be greater than 0."}
            )

        if transaction_type == "o":  # OUT
            if quantity > inventory_item.quantity:
                raise forms.ValidationError(
                    {
                        "quantity": "Cannot use more items than available in inventory."
                    }
                )

        if inventory_item.unit.allow_decimal == False:
            if quantity % 1 != 0:
                raise forms.ValidationError(
                    {"quantity": f"Quantity must be a whole number for {item}"}
                )
        return cleaned_data


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        exclude = ("verification_code",)

    def clean(self):
        cleaned_data = super().clean()
        reorder_point = cleaned_data.get("reorder_point")
        unit = cleaned_data.get("unit")

        if unit is None:
            raise forms.ValidationError({"unit": "Please Select a Unit."})

        inventory_unit = InventoryUnit.objects.get(id=unit.id)

        if inventory_unit.allow_decimal == False:
            if reorder_point % 1 != 0:
                raise forms.ValidationError(
                    {
                        "reorder_point": f"Reorder Point must be a whole number for {unit}"
                    }
                )
        return cleaned_data
