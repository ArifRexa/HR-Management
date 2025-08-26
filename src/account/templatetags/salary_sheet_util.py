import calendar
from datetime import date
from math import floor

from dateutil.relativedelta import relativedelta
from django import template
from django.db.models import Sum
from django.db.models.functions import Abs

from account.models import EmployeeSalary, Invoice, SalarySheet, TDSChallan
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
    
    
    
def employee_tax_by_tds(emp: Employee, month, year):
    """
    calculate employee monthly tds for before year for given year
    """
    start_date = date(year-1, 1,1)
    if 7 <= month <= 12:
        _year = start_date.year
    else:
        _year = start_date.year + 1
    first_day = date(int(_year), int(month), 1)
    last_day = date(int(_year), int(month), calendar.monthrange(year, month)[1])
    salary_sheet = SalarySheet.objects.filter(
        date__range=[first_day, last_day],
    ).first()
    if not salary_sheet:
        return 0
    employee_salary = (
        salary_sheet.employeesalary_set.filter(
            employee=emp,
        )
        .annotate(employee_tds=Abs("loan_emi"))
        .first()
    )
    if not employee_salary:
        return 0
    if employee_salary:
        s = str(employee_salary.tax_loan_total)
        return s[1:] if s.startswith("-") else s
    return 0


@register.simple_tag
def employee_total_tds(obj: FinancialYear, emp: Employee, type="num"):
    tds = TDSChallan.objects.filter(
        employee=emp,
        tds_year=obj,
    )
    total_tds = 0
    for t in tds:
        total_tds += float(employee_tax_by_tds(emp, t.tds_month, t.tds_year.start_date.year))
    if type == "word":
        return num2words(total_tds)
    return total_tds
    start_date = date(obj.start_date.year - 1, 7, 1)
    end_date = date(obj.start_date.year, 6, 30)
    employee_tds = EmployeeSalary.objects.filter(
        employee=emp,
        created_at__range=[start_date, end_date],
    ).aggregate(emi=Abs(Sum("loan_emi")))
    # total_tds = sum(tds.loan_emi for tds in employee_tds)
    # total_tds = total_tds*-1 if total_tds < 0 else total_tds
    total_tds = employee_tds["emi"] or 0
    if type == "word":
        return num2words(total_tds)
    return total_tds


@register.simple_tag
def employee_monthly_tds(emp: Employee, month, year):
    """
    calculate employee monthly tds for before year for given year
    """
    start_date = date(year-1, 1,1)
    if 7 <= month <= 12:
        _year = start_date.year
    else:
        _year = start_date.year + 1
    first_day = date(int(_year), int(month), 1)
    last_day = date(int(_year), int(month), calendar.monthrange(year, month)[1])
    salary_sheet = SalarySheet.objects.filter(
        date__range=[first_day, last_day],
    ).first()
    if not salary_sheet:
        return 0
    employee_salary = (
        salary_sheet.employeesalary_set.filter(
            employee=emp,
        )
        .annotate(employee_tds=Abs("loan_emi"))
        .first()
    )
    if not employee_salary:
        return 0
    if employee_salary:
        s = str(employee_salary.tax_loan_total)
        return s[1:] if s.startswith("-") else s
    return 0


@register.filter
def month_name(value):
    """
    value: integer 1-12
    returns: full month name
    """
    return calendar.month_name[value]
