from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from django.core.exceptions import ValidationError
from django_userforeignkey.models.fields import UserForeignKey
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


class InventoryItem(TimeStampMixin, AuthorMixin):
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

    class Meta:
        verbose_name = "Inventory Transaction"
        verbose_name_plural = "Inventory Transactions"
        permissions = (("can_change_inventory_status", "Can Change Inventory status"),)

    def __str__(self):
        return f"{self.inventory_item.name} | {self.quantity} | {self.transaction_date}"
