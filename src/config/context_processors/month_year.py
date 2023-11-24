from django.utils import timezone


def current_month_year(request):
    month = timezone.now().month
    year = timezone.now().year
    return {
        'month': month,
        'year': year
    }
