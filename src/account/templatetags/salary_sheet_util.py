from datetime import datetime
from math import floor

from django import template
from employee.models import Employee

register = template.Library()


@register.filter
def to_floor(number):
    return floor(number)


@register.filter
def get_account_number(employee: Employee):
    bank_account = employee.bankaccount_set.filter(default=True).first()
    if bank_account:
        return bank_account.account_number
    return 'bank account number not found'


@register.filter
def _total_by_des_type(employee_salary_set):
    total = 0
    for employee_salary in employee_salary_set:
        print(employee_salary.gross_salary)
        total += floor(employee_salary.gross_salary)
    return floor(total)


@register.filter
def _in_dollar(value):
    return value / 80
