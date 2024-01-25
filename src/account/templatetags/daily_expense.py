from django import template
from django.utils import timezone
from account.models import Expense
from django.db.models.functions import Concat
from django.db.models import CharField, Value

register = template.Library()

@register.filter
def daily_sum(queryset):
    return sum(item.get('expense_amount') for item in queryset)

@register.filter
def details_for_expense_group(queryset, date=timezone.now().date):
    details_list = Expense.objects.filter(expanse_group__id=queryset.get('expanse_group__id'), date=date)
    notes = ''
    for details in details_list:
        if details.note != '':
            notes += details.note + ' | '
    
    return notes