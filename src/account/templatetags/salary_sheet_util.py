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
