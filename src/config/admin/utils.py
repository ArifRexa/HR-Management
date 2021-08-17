from django.conf import settings
from django.utils.dateparse import parse_date, parse_datetime


def simple_request_filter(request):
    s_filter = dict([(key, request.GET.get(key)) for key in dict(request.GET) if key not in ['p', 'o', 'e']])
    if s_filter.get('date__gte'):
        s_filter['date__gte'] = parse_datetime(request.GET['date__gte']) if settings.USE_TZ else parse_date(
            request.GET['date__gte'])
    if s_filter.get('date__lt'):
        s_filter['date__lt'] = parse_datetime(request.GET['date__lt']) if settings.USE_TZ else parse_date(
            request.GET['date__lt'])
    return s_filter
