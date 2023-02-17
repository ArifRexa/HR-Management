from django.shortcuts import render
from django.http import JsonResponse
import json
from project_management.models import DailyProjectUpdate
from datetime import datetime, timedelta

from employee.models import Employee
from django.db.models import Sum, Q, FloatField
from django.db.models.functions import Coalesce


# Create your views here.
def get_this_week_hour(request, project_id, hour_date):
    manager_id = request.user.employee.id

    employee = Employee.objects.filter(active=True, project_eligibility=True).annotate(
        total_hour=Coalesce(Sum(
            'dailyprojectupdate_employee__hours',
            filter=Q(
                dailyprojectupdate_employee__project=project_id, 
                dailyprojectupdate_employee__manager=manager_id, 
                dailyprojectupdate_employee__status='approved',
                dailyprojectupdate_employee__created_at__date__lte=hour_date,
                dailyprojectupdate_employee__created_at__date__gte=hour_date-timedelta(days=6),
            ),
        ), 0.0),
    ).exclude(total_hour=0.0).values('id', 'total_hour')

    # final_hour = employee.hours
    # print(final_hour)

            

    # weekly_hour = DailyProjectUpdate.objects.filter(project=project_id, manager=manager_id, status='approved', created_at__gte=datetime.now()-timedelta(days=7)).values_list('hours', 'employee__user__username')
    # print(list(weekly_hour))

    data = {
        'manager_id,':manager_id,
        'weekly_hour':list(employee),
    }
    
    return JsonResponse(data)
    