from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter(name='replace_newline_wth_br')
def replace_text(value):
    return format_html(value.replace('\n', r'<br />'))
