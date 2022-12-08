import json

from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from employee.forms.employee_online import EmployeeStatusForm
from employee.forms.employee_project import EmployeeProjectForm
from employee.models import EmployeeActivity, EmployeeOnline
from employee.models.employee_activity import EmployeeProject
from config.settings import white_listed_ips, employee_ids

# white_listed_ips = ['103.180.244.213', '127.0.0.1', '134.209.155.127', '45.248.149.252']


@require_http_methods(['POST'])
def change_status(request, *args, **kwargs):
    if not get_client_id(request) in white_listed_ips:
        messages.error(request, 'You cannot change your activity status from out site office')
        return redirect('/admin/')

    if str(request.user.employee.id) in employee_ids:
        messages.error(request, 'Management should not use activity status')
        return redirect('/admin/')

    employee_status = EmployeeOnline.objects.get(employee=request.user.employee)
    form = EmployeeStatusForm(request.POST, instance=employee_status)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your status has been change successfully')
        return redirect('/admin/')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('/admin/')


@require_http_methods(['POST'])
def change_project(request, *args, **kwargs):
    if str(request.user.employee.id) in employee_ids:
        messages.error(request, 'Management should not use select or change project')
        return redirect('/admin/')

    employee_project = EmployeeProject.objects.get(employee=request.user.employee)
    form = EmployeeProjectForm(request.POST, instance=employee_project)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your project has been changes successfully')
        return redirect('/admin/')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('/admin/')


def get_client_id(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
