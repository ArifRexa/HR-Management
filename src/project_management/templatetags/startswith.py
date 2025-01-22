from django import template

register = template.Library()


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False

@register.filter(name='divide_by')
def divide_by(value, divisor):
    try:
        return float(value) / float(divisor)
    except (ValueError, ZeroDivisionError):
        return 0.0
    
    
@register.filter(name='create_id')
def create_id(value):
    value = value[1:]
    sanitized = value.split("=")[0].split("__")
    if len(sanitized) > 1:
        id = "__".join(sanitized)
    else:
        id = sanitized[0]
    # print(id)
    return id

@register.filter(name="remove_dash")
def remove_dash(value):
    if not value.startswith("-"):
        return value
    return value[2:]