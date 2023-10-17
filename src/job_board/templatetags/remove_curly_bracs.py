from django import template

register = template.Library()

@register.filter
def remove_curly_bracs(value):
    return value.replace("{", "_").replace("}", "_")