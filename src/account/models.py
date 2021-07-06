from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Sum
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee


class SalarySheet(TimeStampMixin, AuthorMixin):
    date = models.DateField(blank=False)
    festival_bonus = models.BooleanField(default=False)
    total_value = models.FloatField(null=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)


class EmployeeSalary(TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    net_salary = models.FloatField()
    overtime = models.FloatField(null=True)
    project_bonus = models.FloatField(null=True, default=0.0)
    leave_bonus = models.FloatField(null=True, default=0.0)
    festival_bonus = models.FloatField(null=True, default=0.0)
    gross_salary = models.FloatField()
    salary_sheet = models.ForeignKey(SalarySheet, on_delete=models.CASCADE)


class SalaryDisbursement(TimeStampMixin, AuthorMixin):
    disbursement_choice = (
        ('salary_account', 'Salary Account'),
        ('personal_account', 'Personal Account')
    )
    title = models.CharField(max_length=100)
    employee = models.ManyToManyField(Employee)
    disbursement_type = models.CharField(choices=disbursement_choice, max_length=50)


class Expense(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True)
    amount = models.FloatField()
    date = models.DateField(default=timezone.now())
