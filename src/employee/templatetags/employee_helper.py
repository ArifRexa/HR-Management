from django import template
from django.utils import timezone

from employee.models import Employee

register = template.Library()


@register.filter
def get_available_leave(employee: Employee, leave_type: str):
    available_leave = 0
    get_leave_by_type = getattr(employee.leave_management, leave_type)
    print(leave_type, get_leave_by_type)
    if employee.permanent_date:
        total_days_of_permanent = (timezone.now().replace(month=12, day=31).date() - employee.permanent_date).days
        month_of_permanent = round(total_days_of_permanent / 30)
        if month_of_permanent < 12:
            available_leave = (month_of_permanent * get_leave_by_type) / 12
        else:
            available_leave = get_leave_by_type
    return round(available_leave)
