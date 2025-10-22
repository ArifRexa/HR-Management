from django import template
from django.db.models import QuerySet, Sum
from django.utils import timezone
from django.template.loader import get_template
from django.utils.html import format_html
from account.models import EmployeeSalary
from employee.admin.leave import has_friday_between_dates, has_monday_between_dates
from employee.models import Employee
from employee.models.leave.leave import Leave
from settings.models import FinancialYear

register = template.Library()


@register.filter
def get_available_leave(employee: Employee, leave_type: str):
    # TODO : need to replace it with Employee Model method that i've done for Leave -> list -> leave info
    available_leave = 0
    get_leave_by_type = getattr(employee.leave_management, leave_type)
    if employee.permanent_date:
        if employee.resignation_date:
            total_days_of_permanent = (
                employee.resignation_date - employee.permanent_date
            ).days
        else:
            total_days_of_permanent = (
                timezone.now().replace(month=12, day=31).date()
                - employee.permanent_date
            ).days
        month_of_permanent = round(total_days_of_permanent / 30)
        if month_of_permanent < 12:
            available_leave = (month_of_permanent * get_leave_by_type) / 12
        else:
            available_leave = get_leave_by_type

    return round(available_leave)


@register.filter
def sum_employee_salary(employee_salary: QuerySet, target_column: str):
    financial_year = FinancialYear.objects.filter(active=True).first()
    total = employee_salary.filter(
        salary_sheet__date__gte=financial_year.start_date,
        salary_sheet__date__lte=financial_year.end_date,
    ).aggregate(total=Sum(target_column))
    return total["total"] or 0


@register.filter
def sum_employee_salary_with_festival_bonus(employee_salary: QuerySet):
    salary = sum_employee_salary(employee_salary, "gross_salary")
    bonus = sum_employee_salary(employee_salary, "festival_bonus")
    return salary + bonus


@register.filter(name="total_employee_count")
def total_employee_count(result):
    e_ids = {e.employee.id for e in result if e.employee}
    return len(e_ids)


@register.filter(name="total_project_count")
def total_project_count(result):
    e_ids = {e.project.id for e in result if e.project}
    return len(e_ids)


@register.filter(name="total_client_count")
def total_client_count(result):
    projects = {e.project for e in result if e.project}
    client_ids = {i.client.id for i in projects if i.client}
    return len(client_ids)


@register.filter
def divisible_by(value):
    try:
        return value / 4
    except (TypeError, ZeroDivisionError):
        return None


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def leave_details(leave):
    """
    Custom template tag to render leave information HTML.
    Takes a `Leave` instance and returns formatted HTML.
    """
    # Replace `leave.end_date.replace(month=12, day=31)` with your logic
    year_end_date = leave.end_date.replace(month=12, day=31)

    # Use a template to render the leave info
    html_template = get_template("admin/leave/list/col_leave_info.html")
    html_content = html_template.render(
        {
            "casual_passed": leave.employee.leave_passed("casual", year_end_date.year),
            "casual_remain": leave.employee.leave_available(
                "casual_leave", year_end_date
            ),
            "medical_passed": leave.employee.leave_passed(
                "medical", year_end_date.year
            ),
            "medical_remain": leave.employee.leave_available(
                "medical_leave", year_end_date
            ),
        }
    )
    return format_html(html_content)


@register.filter
def total_leave(leave: Leave, data):
    html_template = get_template("admin/leave/list/col_leave_day.html")
    html_content = html_template.render(
        {
            "data": data,
            "leave_day": leave.end_date.strftime("%A"),
            "has_friday": has_friday_between_dates(leave.start_date, leave.end_date),
            "has_monday": leave.applied_leave_type == "emergency_leave",
        }
    )
    return format_html(html_content)


# @register.filter
# def manager_approval(obj):
#     leave_management = LeaveManagement.objects.filter(leave=obj)
#     html_template = get_template("admin/leave/list/col_manager_approval.html")
#     html_content = html_template.render({"leave_management": leave_management})

#     return format_html(html_content)


@register.filter
def leave_status(leave: Leave):
    # Get attachment of leave
    attachments = leave.leaveattachment_set.all()
    if attachments:
        attch_url = attachments[0].attachment.url
    else:
        attch_url = ""

    data = ""
    html_template = get_template("admin/leave/list/col_leave_day.html")

    if leave.status == "pending":
        data = "⏳"
    elif leave.status == "approved":
        data = "✅"
    elif leave.status == "rejected":
        data = "⛔"
    else:
        data = "🤔"

    html_content = html_template.render(
        {
            # 'use_get_display':True,
            "data": data,
            "atch_url": attch_url,
            "message": leave.message,
            "leave_day": leave.end_date.strftime("%A"),
            "has_friday": has_friday_between_dates(leave.start_date, leave.end_date),
            "has_monday": has_monday_between_dates(leave.start_date, leave.end_date),
        }
    )
    return format_html(html_content)
