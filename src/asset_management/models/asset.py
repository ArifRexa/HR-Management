from datetime import timedelta

from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from smart_selects.db_fields import ChainedForeignKey


from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee


class AssetHead(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    depreciation = models.IntegerField(default=0, help_text="In %")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Head"
        verbose_name_plural = "Heads"


class AssetItem(AuthorMixin, TimeStampMixin):
    head = models.ForeignKey(AssetHead, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Vendor(AuthorMixin, TimeStampMixin):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Brand(AuthorMixin, TimeStampMixin):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AssetVariant(AuthorMixin, TimeStampMixin):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Variant"
        verbose_name_plural = "Variants"


class Asset(AuthorMixin, TimeStampMixin):
    STATUS_CHOICES = [("pending", "⌛ Pending"), ("approved", "✔ Approved")]
    date = models.DateField(help_text="Date of purchase", null=True)
    # title = models.CharField(max_length=255, null=True)
    rate = models.FloatField(default=0.00, verbose_name="Purchase Price")
    # addition = models.ManyToManyField(Addition, related_name="asset_additions", null=True, blank=True)
    # category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.SET_NULL, null=True, blank=True
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True
    )
    head = models.ForeignKey(AssetHead, on_delete=models.CASCADE, null=True)
    variant = models.ForeignKey(
        AssetVariant, on_delete=models.SET_NULL, null=True, blank=True
    )
    code = models.SlugField(max_length=50, unique=True)
    description = models.TextField(default="", blank=True)

    is_available = models.BooleanField(default=True)
    # item = models.ForeignKey(
    #     AssetItem, on_delete=models.SET_NULL, null=True, blank=True
    # )
    item = ChainedForeignKey(
        AssetItem,
        chained_field="head",
        chained_model_field="head",
        show_all=False,
        auto_choose=True,
        null=True,
        verbose_name="Category",
    )

    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,  # Add this if you'll be querying by status frequently
    )
    # need_repair = models.BooleanField(default=False)

    # last_assigned = models.DateTimeField(null=True, blank=True)

    # note = models.TextField(null=True, blank=True)

    @property
    def total_amount(self):
        addition_total = 0.00
        for add in self.addition.all():
            addition_total += add.amount
        return addition_total + self.rate

    def __str__(self):
        title = "-"
        if self.item:
            title = self.item.title
        return f"{title} | {self.code}"

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        permissions = [
            ("can_view_asset_status", "Can view asset status"),
            ("can_change_asset_status", "Can change asset status"),
            ("can_view_asset_history", "Can view asset history"),
        ]


class Addition(AuthorMixin, TimeStampMixin):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="addition",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    amount = models.FloatField(default=0.00)
    date = models.DateField(help_text="Date of purchase")

    def __str__(self):
        return self.title


class EmployeeAssignedAsset(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(
        Employee,
        models.CASCADE,
        limit_choices_to={"active": True},
        related_name="assigned_assets",
    )
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="assigned_employees"
    )
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        # return f"{self.employee.full_name} - {self.asset.title}"
        return f"{self.employee.full_name} - {self.asset}"


# class AssetAssignedHistory(AuthorMixin, TimeStampMixin):
#     employee = models.ForeignKey(
#         Employee,
#         models.CASCADE,
#         limit_choices_to={"active": True},
#         related_name="assigned_assets",
#     )
#     asset = models.ForeignKey(
#         Asset, on_delete=models.CASCADE, related_name="assigned_employees"
#     )
#     start_date = models.DateField(default=timezone.now)
#     end_date = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.employee.full_name} - {self.asset.title}"


@receiver(pre_save, sender=EmployeeAssignedAsset)
def asset_assign(sender, instance, **kwargs):
    # Avoid recursive signal calls
    if getattr(instance, "_signal_handled", False):
        return

    # Retrieve the most recent instance for the same employee
    old_instance = (
        sender.objects.filter(employee=instance.employee)
        .order_by("-id")
        .first()
    )

    if old_instance:
        # Update the end_date for the old assignment
        old_instance.end_date = timezone.now() - timedelta(days=1)
        # Temporarily disable signal handling for this save
        old_instance._signal_handled = True
        old_instance.save()

        # Mark the old asset as available
        old_asset = old_instance.asset
        old_asset.is_available = True
        old_asset.save()

    # Mark the new asset as not available
    new_asset = instance.asset
    new_asset.is_available = False
    new_asset.save()

    # Set the flag on the instance to avoid re-triggering
    instance._signal_handled = True


@receiver(pre_delete, sender=EmployeeAssignedAsset)
def asset_unassign(sender, instance, **kwargs):
    asset = instance.asset
    asset.is_available = True
    asset.save()


class EmployeeAsset(Employee):
    class Meta:
        proxy = True
        verbose_name = "Employee Asset"
        verbose_name_plural = "Employee Assets"


class SubAsset(AuthorMixin, TimeStampMixin):
    pass


class PriorityChoices(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    High = "high", "High"


class AssetRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    DONE = "done", "Done"
    IN_PROGRESS = "in_progress", "In Progress"


class AssetRequest(AuthorMixin, TimeStampMixin):
    category = models.ForeignKey(
        AssetItem, on_delete=models.CASCADE, related_name="asset_requests"
    )
    quantity = models.IntegerField(default=1)
    priority = models.CharField(
        max_length=10,
        choices=PriorityChoices.choices,
        default=PriorityChoices.LOW,
    )
    status = models.CharField(
        max_length=15,
        choices=AssetRequestStatus.choices,
        default=AssetRequestStatus.PENDING,
    )
    approved_at = models.DateField(null=True, editable=False)


class AssetRequestNote(AuthorMixin, TimeStampMixin):
    request = models.ForeignKey(
        AssetRequest,
        on_delete=models.CASCADE,
        related_name="asset_request_notes",
    )
    note = models.TextField(null=True, blank=True)


class AssetCategory(AuthorMixin, TimeStampMixin):
    name = models.CharField(
        db_index=True,
        help_text="Table, Chair, Monitor, Keyboard, Mouse, Headphone, RAM, SSD, HDD, GPU",
        max_length=255,
        unique=True,
    )
    serial_short_form_prefix = models.CharField(
        max_length=50,
        help_text="KB, MS, HP, RM, SSD, HDD, GPU",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class AssetBrand(AuthorMixin, TimeStampMixin):
    name = models.CharField(
        db_index=True,
        help_text="HP, LG, Samsung, DELL, etc.",
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.name


class RAMSize(AuthorMixin, TimeStampMixin):
    ram_capacity = models.CharField(
        max_length=10,
        unique=True,
        help_text="RAM capacity in GB.",
    )

    def __str__(self):
        return self.ram_capacity


class MonitorSize(AuthorMixin, TimeStampMixin):
    display_size = models.CharField(
        max_length=10,
        unique=True,
        help_text="Screen size in inches e.g., 24",
    )

    def __str__(self):
        return self.display_size


class SSDorHDDSize(AuthorMixin, TimeStampMixin):
    storage_capacity = models.CharField(
        max_length=10,
        unique=True,
        help_text="SSD or HDD capacity in GB. exm: 32",
    )

    def __str__(self):
        return f"{self.storage_capacity}GB"


class ProcessorData(AuthorMixin, TimeStampMixin):
    processor_info = models.CharField(
        max_length=255,
        unique=True,
        help_text="for Intel: i5-10th or i7-13th",
    )

    class Meta:
        verbose_name_plural = "Processors"
        verbose_name = "Processor"

    def __str__(self):
        return self.processor_info


class FixedAsset(AuthorMixin, TimeStampMixin):
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        to=AssetCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fixed_assets",
    )
    brand = models.ForeignKey(
        to=AssetBrand,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fixed_assets",
    )

    # General specifications
    core = models.ForeignKey(
        to=ProcessorData,
        on_delete=models.SET_NULL,
        related_name="fixed_asset_core",
        blank=True,
        null=True,
        help_text="Processor details: i5-13th",
    )
    ram_size = models.ForeignKey(
        to=RAMSize,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fixed_assets",
    )
    storage_size = models.ForeignKey(
        to=SSDorHDDSize,
        on_delete=models.SET_NULL,
        related_name="fixed_asset_storage",
        blank=True,
        null=True,
        help_text="Storage size in GB.",
    )
    display_size = models.ForeignKey(
        to=MonitorSize,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fixed_assets",
    )
    gpu = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="GPU model, if any",
    )
    other_specs = models.TextField(
        blank=True,
        null=True,
        help_text="Any additional configuration",
    )

    serial = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    asset_id = models.CharField(
        max_length=100,
        editable=False,
    )
    vendor = models.ForeignKey(
        to=Vendor,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fixed_assets",
    )
    purchase_date = models.DateField()
    warranty_duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Warranty duration in months",
    )

    def __str__(self):
        if self.category.name in ["Table", "Chair"]:
            return self.asset_id
        field_map = {
            "SSD": self.storage_size,
            "HDD": self.storage_size,
            "GPU": self.gpu,
            "Processor": self.core.processor_info if self.core else None,
            "Monitor": self.display_size.display_size
            if self.display_size
            else None,
            "RAM": self.ram_size.ram_capacity if self.ram_size else None,
        }
        items = [
            self.brand.name if self.brand else None,
            str(field_map.get(self.category.name, "")),
            self.other_specs,
        ]
        fixed_asset = ", ".join([item for item in items if item])
        return f"{self.asset_id}({fixed_asset})"


class CasingBrand(AuthorMixin, TimeStampMixin):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Brand name, HP, DELL, etc.",
    )

    def __str__(self):
        return self.name


class CPU(AuthorMixin, TimeStampMixin):
    casing = models.ForeignKey(
        to=CasingBrand,
        on_delete=models.SET_NULL,
        related_name="cpu_casings",
        null=True,
    )
    asset_id = models.CharField(
        max_length=100,
        editable=False,
    )
    processor = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cpu_processor",
        limit_choices_to={"category__name": "Processor"},
    )
    ram1 = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cpu_ram1",
        limit_choices_to={"category__name": "RAM"},
    )
    ram2 = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cpu_ram2",
        limit_choices_to={"category__name": "RAM"},
    )
    ssd = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cpu_ssd",
        limit_choices_to={"category__name": "SSD"},
    )
    hdd = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cpu_hdd",
        limit_choices_to={"category__name": "HDD"},
    )
    gpu = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cpu_gpu",
        limit_choices_to={"category__name": "GPU"},
    )

    def __str__(self):
        items = [
            self.casing,
            self.processor,
            self.ram1,
            self.ram2,
            self.ssd,
            self.hdd,
            self.gpu,
        ]
        cpu = ", ".join([str(item) for item in items if item])
        return f"{self.asset_id}({cpu})"


class EmployeeFixedAsset(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(
        to=Employee,
        on_delete=models.CASCADE,
        related_name="employee_fixed_assets_employee",
    )
    table = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"category__name": "Table"},
        related_name="employee_fixed_asset_table",
    )
    chair = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"category__name": "Chair"},
        related_name="employee_fixed_asset_chair",
    )
    monitor1 = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"category__name": "Monitor"},
        related_name="employee_fixed_asset_monitor1",
    )
    monitor2 = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"category__name": "Monitor"},
        related_name="employee_fixed_asset_monitor2",
    )
    cpu = models.OneToOneField(
        to=CPU,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employee_fixed_asset_cpu",
    )
    keyboard = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"category__name": "Keyboard"},
        related_name="employee_fixed_asset_keyboard",
    )
    mouse = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"category__name": "Mouse"},
        related_name="employee_fixed_asset_mouse",
    )
    headphone = models.OneToOneField(
        to=FixedAsset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"category__name": "Headphone"},
        related_name="employee_fixed_asset_headphone",
    )
    extra = models.TextField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    
    
    class Meta:
        permissions = [
            ("cal_view_all_employee_asset", "Can view all employee fixed asset"),
        ]


class AssetAssignmentLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    asset = models.ForeignKey(FixedAsset, on_delete=models.CASCADE, null=True, blank=True)
    cpu = models.ForeignKey(CPU, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(
        max_length=10, choices=[("ASSIGN", "Assign"), ("RETURN", "Return")]
    )
    date = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.action} {self.asset} to {self.employee} @ {self.date:%Y-%m-%d %H:%M}"

