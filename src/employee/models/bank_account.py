from django.db import models

from employee.models import Employee
from settings.models import Bank


class BankAccount(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.RESTRICT)
    account_number = models.CharField(max_length=100)
    default = models.BooleanField(default=False)
