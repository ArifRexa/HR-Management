import calendar
from math import floor

from dateutil.relativedelta import relativedelta
from django import template
from django.db.models import Sum, functions

from account.models import EmployeeSalary, Invoice
from employee.models import Employee
from settings.models import FinancialYear

register = template.Library()


@register.filter
def to_floor(number):
    return floor(number)


@register.filter
def get_account_number(employee: Employee):
    bank_account = employee.bankaccount_set.filter(default=True).first()
    if bank_account:
        return bank_account.account_number
    return "bank account number not found"


@register.filter(name="strip_last_newline")
def strip_last_newline(value):
    if not value:
        return value
    if value.endswith("\n"):
        value = value[:-1]
    return value.replace("\n", "<br />")


@register.filter(name="last_week")
def last_week(value):
    return value - relativedelta(days=6)


@register.filter
def _total_by_des_type(employee_salary_set):
    total = 0
    for employee_salary in employee_salary_set:
        total += floor(employee_salary.gross_amount)
    return floor(total)


@register.filter
def _total_bonus(employee_salary_set):
    total = 0
    for employee_salary in employee_salary_set:
        total += floor(employee_salary.festival_bonus)
    return floor(total)


@register.filter
def _total_festival_bonus(employee_festival_bonus_set):
    return floor(
        employee_festival_bonus_set.aggregate(Sum("amount"))["amount__sum"]
    )

    total = 0
    for employee_festival_bonus in employee_festival_bonus_set:
        total += floor(employee_festival_bonus.amount)
    return floor(total)


@register.filter
def _in_dollar(value):
    return value / 80


@register.filter
def sum_invoice_details(invoice: Invoice, column: str):
    return invoice.invoicedetail_set.all().aggregate(total=Sum(column))["total"]


from num2words import num2words


@register.filter
def abs(value):
    try:
        return abs(value)
    except TypeError:
        return value


@register.simple_tag
def employee_total_tds(obj: FinancialYear, emp: Employee, type="num"):
    total_tds = EmployeeSalary.objects.filter(
        employee=emp,
        created_at__range=[obj.start_date, obj.end_date],
    )
    total_tds = total_tds.aggregate(total_tds=functions.Abs(Sum("loan_emi")))
    if type == "word":
        return num2words(total_tds.get("total_tds", 0) or 0)
    return total_tds.get("total_tds", 0) or 0


@register.simple_tag
def employee_monthly_tds(emp: Employee, month, year):
    if 7 <= month <= 12:
        year = year
    else:
        year = year + 1
    tds = (
        EmployeeSalary.objects.filter(
            employee=emp, created_at__year=year, created_at__month=month
        )
        .annotate(employee_tds=functions.Abs("loan_emi"))
        .first()
    )
    return tds.employee_tds if tds else 0


@register.filter
def month_name(value):
    """
    value: integer 1-12
    returns: full month name
    """
    return calendar.month_name[value]
