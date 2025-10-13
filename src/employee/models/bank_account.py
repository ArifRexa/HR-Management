from tabnanny import verbose
from typing import Iterable, Optional
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from employee.models import Employee
from settings.models import Bank


# class BEFTN(models.Model):
#     originating_bank_routing_number = models.CharField(max_length=100)
#     originating_bank_account_number = models.CharField(max_length=100)
#     originating_bank_account_name = models.CharField(max_length=255,null=True,blank=True)
#     routing_no = models.CharField(max_length=100,null=True,blank=True)

#     class Meta:
#         app_label = 'account'
#         verbose_name_plural = "BEFTN"


class BankAccount(models.Model):
    employee = models.ForeignKey(Employee,
                                 limit_choices_to={'active': True},
                                 on_delete=models.CASCADE
                                 )
    bank = models.ForeignKey(Bank, on_delete=models.RESTRICT)
    account_number = models.CharField(max_length=100)
    default = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.bank.name
    
    class Meta:
        permissions = (
            ('can_edit_all_bank_account', 'Can edit all bank account', ),
            ('can_approve_bank_account_info', 'Can approve bank account info', ),
        )
        unique_together = ('employee', 'bank')


# Set the latest one default and make everything default false
@receiver(post_save, sender=BankAccount)
def make_default(sender, instance, **kwargs):
    if instance.default:
        sender.objects.filter(
            employee=instance.employee, 
            default=True,
        ).exclude(
            id=instance.id,
        ).update(
            default=False,
        )

