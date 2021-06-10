from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Sum

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee


class SalarySheet(TimeStampMixin, AuthorMixin):
    date = models.DateField(blank=False)
    total_value = models.FloatField(null=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)


class EmployeeSalary(TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    net_salary = models.FloatField()
    overtime = models.FloatField(null=True)
    project_bonus = models.FloatField(null=True)
    leave_bonus = models.FloatField(null=True)
    gross_salary = models.FloatField()
    salary_sheet = models.ForeignKey(SalarySheet, on_delete=models.CASCADE)
