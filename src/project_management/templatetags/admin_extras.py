from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a variable key
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def get_attr(obj, attr):
    """
    Get an attribute from an object dynamically
    """
    if obj and hasattr(obj, attr):
        return getattr(obj, attr)
    return None

@register.simple_tag
def get_project_date_key(project_id, date):
    """
    Create a key in the format 'project_id_date' for lookup
    """
    return f"{project_id}_{date.strftime('%Y-%m-%d')}"