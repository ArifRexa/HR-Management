from django import template

register = template.Library()


@register.filter(name='is_query')
def is_query(param, value):
    if not param:
        return False
    if param.startswith("-") and str(value) in param:
        return True
    return str(value) in param

    