from django import template
register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key)

@register.filter
def getattr(obj, attr):
    return getattr(obj, attr, 'N/A') if obj else 'N/A'