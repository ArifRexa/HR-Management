from django import template
from django.utils.html import format_html
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from urllib.parse import urlparse

register = template.Library()


@register.filter(name='replace_newline_wth_br')
def replace_text(value):
    return format_html(value.replace('\n', r'<br />'))


@register.filter(name="check_valid_url")
def check_valid_url(value):
    validate_url = URLValidator()
    try:
        validate_url(value)
    except ValidationError as e:
        return False

    return True


@register.simple_tag
def link_icon(url):
    if not url:
        return ""
    # if not check_valid_url(url):
    #     pass
    icons = {
        'github': format_html('<i class="fa-brands fa-github text-dark" style="color:black"></i>'),
        'figma': format_html('<i class="fa-brands fa-figma text-dark" style="color:black"></i>'),
        'trello': format_html('<i class="fa-brands fa-trello text-dark" style="color:black"></i>'),
        'default': format_html('<i class="fa-solid fa-globe text-dark" style="color:black"></i>'),
    }
    domain = urlparse(url).netloc
    domain_split = domain.split(".")
    domain_name = ""
    icon_name = ""
    if len(domain_split) == 4:
        domain_name = f"{domain_split[2]}.{domain_split[3]}"
        icon_name = domain_split[2]
    elif len(domain_split) == 3:
        domain_name = f"{domain_split[1]}.{domain_split[2]}"
        icon_name = domain_split[1]
    elif len(domain_split) == 2:
        domain_name = f"{domain_split[0]}.{domain_split[1]}"
        icon_name = domain_split[0]

    if domain_name in url and icons.get(icon_name):
        return icons.get(icon_name)
    return icons["default"]
