from math import floor

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat
from num2words import num2words
import calendar

from employee.models import Employee

register = template.Library()


@register.filter
def num_to_word(number):
    return num2words(number)


@register.filter
def percentage(number, arg):
    try:
        percentage_number = ((number) / 100) * arg
        return intcomma(floatformat(percentage_number, 2))
    except:
        return 0.00


@register.filter
def addition(number, addition_number):
    try:
        # Convert inputs to float to ensure the addition operation works
        return float(number) + float(addition_number)
    except (ValueError, TypeError):
        # Handle cases where conversion fails or inputs are not numbers
        return 0

@register.filter
def int_to_month(value):
    if not isinstance(value, int) or value < 1 or value > 12:
        return "Invalid Month"
    return calendar.month_name[value]
