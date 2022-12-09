from django.conf import settings
from django.utils.dateparse import parse_date, parse_datetime
from config.settings import white_listed_ips, employee_ids
from django.contrib import messages
from django.shortcuts import redirect
import functools


def simple_request_filter(request):
    s_filter = dict(
        [(key, request.GET.get(key)) for key in dict(request.GET) if key not in ['p', 'o', 'e', 'q', 'all']])
    if s_filter.get('date__gte'):
        s_filter['date__gte'] = parse_date(request.GET['date__gte']) if parse_date(
            request.GET['date__gte']) is not None else parse_datetime(request.GET['date__gte'])
    if s_filter.get('date__lt'):
        s_filter['date__lt'] = parse_date(request.GET['date__lt']) if parse_date(
            request.GET['date__lt']) is not None else parse_datetime(request.GET['date__lt'])
    return s_filter


def get_client_id(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Additional functions and decorators for ip check and Bypass for Management
def white_listed_ip_check(view_func, redirect_url="/admin/"):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not get_client_id(request) in white_listed_ips:
            messages.error(request, 'You cannot change your activity status from out site office')
            return redirect(redirect_url)
        return view_func(request, *args, **kwargs)

    return wrapper


def not_for_management(view_func, redirect_url="/admin/"):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if str(request.user.employee.id) in employee_ids:
            messages.error(request, 'Management should not use activity status')
            return redirect(redirect_url)
        return view_func(request, *args, **kwargs)

    return wrapper
