from django import template
from django.utils.html import format_html
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

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
