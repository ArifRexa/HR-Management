from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from django.core.exceptions import ValidationError
from django_userforeignkey.models.fields import UserForeignKey
from django.utils.crypto import get_random_string


TRANSACTION_CHOICES = [
    ("i", "IN"),
    ("o", "OUT"),
]


class InventoryUnit(TimeStampMixin, AuthorMixin):
    unit_name = models.CharField(max_length=50)
    allow_decimal = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Inventory Item Unit"
        verbose_name_plural = "Inventory Item Units"

    def __str__(self):
        return self.unit_name


class InventoryItemHead(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Item Head"
        verbose_name_plural = "Item Heads"

    def __str__(self):
        return self.title

class InventoryItem(TimeStampMixin, AuthorMixin):
    # head = models.ForeignKey(InventoryItemHead, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    reorder_point = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=5
    )
    unit = models.ForeignKey(InventoryUnit, on_delete=models.CASCADE, null=True)
    
    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    def __str__(self):
        return self.name


class InventoryTransaction(TimeStampMixin, AuthorMixin):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    transaction_date = models.DateField(default=timezone.now)
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_CHOICES)
    note = models.TextField(null=True, blank=True)
    status = models.CharField(
        choices=(("pending", "Pending"), ("approved", "Approved")),
        default="pending",
        max_length=10,
    )
    updated_by = UserForeignKey(auto_user_add=True, verbose_name="Updated By",
                                related_name="%(app_label)s_%(class)s_update_by")
    
    verification_code = models.CharField(max_length=50, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = get_random_string(length=6).lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Inventory Transaction"
        verbose_name_plural = "Inventory Transactions"
        permissions = (("can_change_inventory_status", "Can Change Inventory status"),)

    def __str__(self):
        return f"{self.inventory_item.name} | {self.quantity} | {self.transaction_date}"



class InventorySummary(InventoryTransaction):
    
    
    class Meta:
        proxy = True
        verbose_name = "Inventory Summary"
        verbose_name_plural = "Inventory Summary"