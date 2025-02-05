from django import template
from datetime import datetime

register = template.Library()


# @register.filter(name='get_item')
# def get_item(dictionary, datas):
#     total_minutes = 0
#     i = 0
#     today = datetime.today().strftime('%Y-%m-%d')  # Get today's date as a string
#
#     for date, data in datas.items():
#         if date == today:  # Skip today's date
#             continue
#         minutes = int(data.get("inside_time_minute", 0))  # Get minutes, default to 0
#         total_minutes += minutes
#         if minutes > 0:
#             i += 1
#
#     if i == 0:  # Prevent division by zero
#         return 0, "0h : 0m (0)"
#
#     i = i-1
#     per_day_minutes = int(total_minutes / i)
#     total_hours = per_day_minutes // 60
#     remaining_minutes = per_day_minutes % 60
#
#     decimal_time = total_hours + (remaining_minutes / 60)  # Convert to float
#
#     return decimal_time, f"{total_hours}h : {remaining_minutes}m ({i})"



@register.filter(name='get_item')
def get_item(dictionary, datas):
    total_minutes = 0
    i = 0
    today = datetime.today().strftime('%Y-%m-%d')  # Get today's date as a string
    used_dates = []  # List to store the dates used in calculation

    for date, data in datas.items():
        if date == today:  # Skip today's date
            continue
        minutes = int(data.get("inside_time_minute", 0))  # Get minutes, default to 0
        total_minutes += minutes
        if minutes > 0:
            i += 1
            used_dates.append(date)  # Store the date

    if i == 0:  # Prevent division by zero
        return 0, "0h : 0m (0)", []

    per_day_minutes = int(total_minutes / i)
    total_hours = per_day_minutes // 60
    remaining_minutes = per_day_minutes % 60

    decimal_time = total_hours + (remaining_minutes / 60)  # Convert to float

    return decimal_time, f"{total_hours}h : {remaining_minutes}m ({i})", used_dates