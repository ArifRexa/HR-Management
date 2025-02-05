from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, datas):
    total_minutes = 0

    for date, data in datas.items():
        hours = int(data.get("inside_time_hour", 0))  # Get hours, default to 0
        minutes = int(data.get("inside_time_minute", 0))  # Get minutes, default to 0

        total_minutes += (hours * 60) + minutes  # Convert hours to minutes and sum up

    total_hours = total_minutes // 60  # Get total hours
    remaining_minutes = total_minutes % 60  # Get remaining minutes

    return f"{total_hours}h : {remaining_minutes}m"
# def get_item(dictionary, datas):
#     total_avg_inside = 0
#
#     for date, data in datas.items():
#         total_min = int(data.get("inside_time_minute")) if data.get("inside_time_minute") else 0
#         total_avg_inside += int(data.get("inside_time_hour")) if data.get("inside_time_hour") else 0
#     return total_avg_inside
