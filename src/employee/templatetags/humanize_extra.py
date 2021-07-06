from math import floor

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from num2words import num2words

from employee.models import Employee

register = template.Library()


@register.filter
def num_to_word(number):
    return num2words(number)


@register.filter
def percentage(number, arg):
    return intcomma((number / 100) * arg)



