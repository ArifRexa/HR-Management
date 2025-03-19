from user_agents import parse
from datetime import date, timedelta

def get_device_name(request):
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    if "Mobile" in user_agent:
        device_type = "Mobile"
    elif "Tablet" in user_agent:
        device_type = "Tablet"
    elif "Windows" in user_agent or "Macintosh" in user_agent or "Linux" in user_agent:
        device_type = "Desktop"
    else:
        device_type = "Unknown"

    return device_type


def get_browser_name(request):
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    parsed_user_agent = parse(user_agent)
    return parsed_user_agent.browser.family


def get_location_by_ip(request):
    import requests

    ip = request.META.get("REMOTE_ADDR")
    response = requests.get(f"https://ipinfo.io/{ip}/json")
    data = response.json()

    location = (
        data.get("city", "Unknown Location")
        + ", "
        + data.get("country", "Unknown Country")
    )
    return location


def get_ip_address(request):
    return request.META.get("REMOTE_ADDR")


def get_operating_system(request):
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    parsed_user_agent = parse(user_agent)
    return parsed_user_agent.os.family



def get_week_date_range(week_number=1):
    """
    Calculate the Monday to Friday date range for a given week number.

    :param week_number: 
        - 1 for the current week
        - 2 for the last week
        - 3 for two weeks ago, etc.
    :return: A tuple containing (monday_date, friday_date)
    """
    today = date.today()
    
    # Calculate this week's Monday
    this_week_monday = today - timedelta(days=today.weekday())

    # Adjust for the given week number (1 = current week, 2 = last week, etc.)
    target_monday = this_week_monday - timedelta(weeks=week_number - 1)
    target_friday = target_monday + timedelta(days=4)

    return target_monday, target_friday