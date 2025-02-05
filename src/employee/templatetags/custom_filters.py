from django import template

register = template.Library()


# @register.filter(name='get_item')
# def get_item(dictionary, datas):
#     total_minutes = 0
#     i = 0
#
#     for date, data in datas.items():
#         minutes = int(data.get("inside_time_minute", 0))  # Get minutes, default to 0
#         total_minutes += minutes
#         if minutes > 0 :
#             i += 1
#     per_day_minutes = int(total_minutes/i)
#     total_hours = per_day_minutes // 60  # Convert minutes to hours
#     remaining_minutes = per_day_minutes % 60  # Get remaining minutes
#
#     return f"{total_hours}h : {remaining_minutes}m ({i})"

@register.filter(name='get_item')
def get_item(dictionary, datas):
    total_minutes = 0
    i = 0

    for date, data in datas.items():
        minutes = int(data.get("inside_time_minute", 0))  # Get minutes, default to 0
        total_minutes += minutes
        if minutes > 0:
            i += 1

    if i == 0:  # Prevent division by zero
        return 0, "0h : 0m (0)"

    per_day_minutes = int(total_minutes / (i-1))
    total_hours = per_day_minutes // 60
    remaining_minutes = per_day_minutes % 60

    decimal_time = total_hours + (remaining_minutes / 60)  # Convert to float

    return decimal_time, f"{total_hours}h : {remaining_minutes}m ({i})"