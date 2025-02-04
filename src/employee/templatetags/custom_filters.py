from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, datas):
    total_avg_inside = ""

    for date, data in datas.items():
        total_avg_inside += data.get('inside_time_hour') if data.get('inside_time_hour') else "0"
    return total_avg_inside
