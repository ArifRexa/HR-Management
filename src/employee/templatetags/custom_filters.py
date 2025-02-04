from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, datas):
    total_avg_inside = 0

    for date, data in datas.items():
        total_avg_inside += int(data.get('inside_time')) if data.get('inside_time') else 0
    return total_avg_inside
