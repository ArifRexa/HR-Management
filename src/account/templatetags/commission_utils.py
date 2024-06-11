from django import template
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce
from django.utils.html import format_html

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


# @register.filter
# def total_due(employee: Employee):
#     prev_paid = total_paid_amount(employee)
#     projects = Project.objects.filter(on_boarded_by=employee).all()
#     total_due_amount = 0.0
#     for project in projects:
#         total_payment = 0.0
#         for index, income in enumerate(project.income_set.filter(status='approved').all()):
#             print(income.project, "income: ", income.payment, " Status : ", income.status)
#             total_payment += income.payment
#             if index == 3:
#                 break
#         total_due_amount += (total_payment / 100) * 5
#     return total_due_amount - prev_paid


# @register.filter
# def total_due_projects(employee: Employee):
#     html = ""
#     projects = Project.objects.filter(on_boarded_by=employee).all()
#     for project in projects:
#         total_payment = 0.0
#         for index, income in enumerate(project.income_set.filter(status='approved').all()):
#             total_payment += income.payment
#             if index == 3:
#                 break
#         if total_payment > 0:
#             paid = project.projectcommission_set.aggregate(total=Coalesce(Sum('payment'), 0, output_field=FloatField()))
#             due = ((total_payment / 100) * 5) - paid['total']
#             html += f"<li>{project} | {due}</li>"
#     return format_html(html)
