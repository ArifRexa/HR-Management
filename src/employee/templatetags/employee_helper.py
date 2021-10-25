from django import template
from django.utils import timezone

from employee.models import Employee

register = template.Library()


@register.filter
def get_available_leave(employee: Employee, leave_type: str):
    available_leave = 0
    get_leave_type = getattr(employee.leave_management, leave_type)
    if employee.permanent_date:
        month_of_permanent = (timezone.now().year - employee.permanent_date.year) * 12 + (
                timezone.now().month - employee.permanent_date.month)
        available_leave = (month_of_permanent / get_leave_type) * get_leave_type
    return available_leave
