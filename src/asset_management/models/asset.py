from uuid import uuid4

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin

from employee.models import Employee


class AssetCategory(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Asset(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)

    code = models.SlugField(max_length=50, unique=True)
    description = models.TextField(default='')
    
    is_available = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    need_repair = models.BooleanField(default=False)

    last_assigned = models.DateTimeField(null=True, blank=True)

    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} | {self.code}"



class EmployeeAssignedAsset(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, models.CASCADE, limit_choices_to={"active": True})
    asset = models.ForeignKey(Asset, models.CASCADE, limit_choices_to={"is_available":True})

    def __str__(self):
        return f"{self.employee.full_name} - {self.asset.title}"


@receiver(pre_save, sender=EmployeeAssignedAsset)
def assset_assign(sender, instance, update_fields=None, **kwargs):
    old_instance = sender.objects.filter(id=instance.id).first()

    # TODO: Handle asset assign date here
    
    if old_instance:
        old_asset = old_instance.asset
        old_asset.is_available = True
        old_asset.save()
    
    new_asset = instance.asset
    new_asset.is_available = False
    new_asset.save()


@receiver(pre_delete, sender=EmployeeAssignedAsset)
def asset_unassign(sender, instance, **kwargs):
    asset = instance.asset
    asset.is_available = True
    asset.save()


# class EmployeeAsset(Employee):
#     class Meta:
#         proxy=True


class SubAsset(AuthorMixin, TimeStampMixin):
    pass
