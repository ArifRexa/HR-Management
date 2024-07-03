from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def sum_project_hours(context, client_data):
    """
    Sum the total_project_hours for each key in client_data.
    """
    return sum(key.total_project_hours for key, value in client_data.items())
    

@register.simple_tag(takes_context=True)
def total_rowspan(context, client_data):
    """
    Return the total number of rows in client_data.
    """
    return sum(len(value) for key, value in client_data.items())
    
