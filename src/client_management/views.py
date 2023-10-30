from django.shortcuts import render
from icecream import ic

from project_management.models import Project, DailyProjectUpdate
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.db.models import Count
from django.db.models import Func
from django.db.models import Value, JSONField


class TruncDate(Func):
    function = 'DATE'
    template = '%(function)s(%(expressions)s)'


# Create your views here.
def get_project_updates(request, project_hash):
    print(project_hash)
    from_date, to_date = request.GET.get('from-date'), request.GET.get('to-date')
    ic(from_date, to_date)
    project_obj = Project.objects.get(identifier=project_hash)
    daily_updates = DailyProjectUpdate.objects.filter(project=project_obj)
    if from_date is not None and to_date is not None:
        daily_updates = daily_updates.filter(created_at__date__lte=to_date, created_at__date__gte=from_date)
    distinct_dates = daily_updates.values('created_at__date').distinct()


    daily_update_list = []
    for u_date in distinct_dates:
        obj = {'created_at':u_date.get('created_at__date').strftime("%d-%m-%Y")}
        # ic(u_date, u_date.get('created_at__date'))
        updates = []
        time = 0
        for update in daily_updates.filter(created_at__date=u_date.get('created_at__date')):
            if update.updates_json is not None:
                updates.extend(update.updates_json)
            # if update.hours
                time += update.hours
        obj['update'] = updates
        obj['total_hour'] = time

        daily_update_list.append(obj)

    # ic(daily_update_list)

    out_dict = {
        'project': project_obj,
        'daily_updates': daily_update_list,
    }

    return render(request, 'client_management/project_details.html', out_dict)