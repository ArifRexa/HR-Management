from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """
    Allows template to access dict keys stored as tuples: (project_id, 'YYYY-MM-DD')
    key arrives as: "projectid-YYYY-MM-DD"
    """
    if "-" in key:
        project_id, date_str = key.split("-", 1)
        try:
            project_id = int(project_id)
        except:
            pass
        return d.get((project_id, date_str))
    return d.get(key)


@register.filter
def getattr(obj, attr):
    return getattr(obj, attr, 'N/A') if obj else 'N/A'
