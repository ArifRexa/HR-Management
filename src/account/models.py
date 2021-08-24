from math import floor

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Sum
from django.utils import timezone

from django.conf import settings
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee
from project_management.models import Project


class SalarySheet(TimeStampMixin, AuthorMixin):
    date = models.DateField(blank=False)
    festival_bonus = models.BooleanField(default=False)
    total_value = models.FloatField(null=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    @property
    def total(self):
        return floor(self.employeesalary_set.aggregate(Sum('gross_salary'))['gross_salary__sum'])


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


class ExpenseCategory(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Expense(TimeStampMixin, AuthorMixin):
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.RESTRICT)
    note = models.TextField(null=True, blank=True)
    amount = models.FloatField()
    date = models.DateField(default=timezone.now)


class ExpanseAttachment(TimeStampMixin, AuthorMixin):
    expanse = models.ForeignKey(Expense, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='uploads/expanse/%y/%m')


class Income(TimeStampMixin, AuthorMixin):
    STATUS_CHOICE = (
        ('pending', '⌛ Pending'),
        ('approved', '✔ Approved')
    )
    project = models.ForeignKey(Project, on_delete=models.RESTRICT, limit_choices_to={'active': True})
    hours = models.FloatField()
    hour_rate = models.FloatField(default=10.0)
    payment = models.FloatField()
    date = models.DateField(default=timezone.now)
    note = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')

    def save(self, *args, **kwargs):
        self.payment = self.hours * (self.hour_rate * 80)
        super(Income, self).save(*args, **kwargs)


class Fund(TimeStampMixin, AuthorMixin):
    date = models.DateField()
    amount = models.FloatField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
