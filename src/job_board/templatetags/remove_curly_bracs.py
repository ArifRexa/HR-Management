from django import template

register = template.Library()

@register.filter
def remove_curly_bracs(value):
    try:
        return value.replace("{", "_").replace("}", "_")
    except:
        return None