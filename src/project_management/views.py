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
    ).exclude(total_hour=0.0).values('id', 'full_name', 'total_hour')

    totalHours = sum(hour['total_hour'] for hour in employee)

    employeeList = filter(lambda emp: emp['id'] != manager_id, employee)


    data = {
        'manager_id':manager_id,
        'weekly_hour':list(employeeList),
        'total_project_hours': totalHours
    }

    return JsonResponse(data)


def slack_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    return JsonResponse({'code': code, 'state': state})
