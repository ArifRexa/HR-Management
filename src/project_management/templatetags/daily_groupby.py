from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def sum_project_hours(context, client_data):
    """
    Sum the total_project_hours for each key in client_data.
    """
    total = sum(key.total_project_hours for key, value in client_data.items())
    return total
