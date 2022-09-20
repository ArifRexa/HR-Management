from django import template
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce

from account.models import ProjectCommission, Income
from employee.models import Employee
from project_management.models import Project

register = template.Library()


@register.filter
def total_paid(employee: Employee):
    return total_paid_amount(employee)


def total_paid_amount(employee):
    return ProjectCommission.objects.filter(employee=employee).aggregate(
        total=Coalesce(Sum('payment'), 0, output_field=FloatField()))['total']


@register.filter
def total_due(employee: Employee):
    prev_paid = total_paid_amount(employee)
    projects = Project.objects.filter(on_boarded_by=employee, active=True).all()
    total_due_amount = 0.0
    for project in projects:
        total_hours = 0.0
        for index, hour in enumerate(project.projecthour_set.all()):
            total_hours += hour.hours
            if index == 3:
                break
        total_due_amount += total_hours * 10
    return total_due_amount - prev_paid
