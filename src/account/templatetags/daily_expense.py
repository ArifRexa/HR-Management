from django import template

register = template.Library()

@register.filter
def daily_sum(queryset):
    return sum(item.get('expense_amount') for item in queryset)