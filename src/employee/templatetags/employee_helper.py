from django import template
from django.db.models import QuerySet, Sum
from django.utils import timezone

from account.models import EmployeeSalary
from employee.models import Employee
from settings.models import FinancialYear

register = template.Library()


@register.filter
def get_available_leave(employee: Employee, leave_type: str):
    # TODO : need to replace it with Employee Model method that i've done for Leave -> list -> leave info
    available_leave = 0
    get_leave_by_type = getattr(employee.leave_management, leave_type)
    if employee.permanent_date:
        if employee.resignation_date:
            total_days_of_permanent = (employee.resignation_date - employee.permanent_date).days
        else:
            total_days_of_permanent = (timezone.now().replace(month=12, day=31).date() - employee.permanent_date).days
        month_of_permanent = round(total_days_of_permanent / 30)
        if month_of_permanent < 12:
            available_leave = (month_of_permanent * get_leave_by_type) / 12
        else:
            available_leave = get_leave_by_type

    return round(available_leave)


@register.filter
def sum_employee_salary(employee_salary: QuerySet, target_column: str):
    financial_year = FinancialYear.objects.filter(active=True).first()
    total = employee_salary.filter(salary_sheet__date__gte=financial_year.start_date,
                                   salary_sheet__date__lte=financial_year.end_date).aggregate(total=Sum(target_column))
    return total['total']
