import json

import datetime

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from employee.forms.employee_online import EmployeeStatusForm
from employee.forms.employee_project import EmployeeProjectForm
from employee.forms.employee_feedback import EmployeeFeedbackForm
from employee.models import EmployeeActivity, EmployeeOnline, EmployeeFeedback
from employee.models.employee_activity import EmployeeProject
from config.admin.utils import white_listed_ip_check, not_for_management
# white_listed_ips = ['103.180.244.213', '127.0.0.1', '134.209.155.127', '45.248.149.252']


@white_listed_ip_check
@require_http_methods(['POST', 'GET'])
@login_required(login_url='/admin/login/')
@not_for_management
def change_status(request, *args, **kwargs):
    employee_status = EmployeeOnline.objects.get(employee=request.user.employee)

    if request.method == 'POST':
        form = EmployeeStatusForm(request.POST, instance=employee_status)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your status has been change successfully')
            return redirect('/admin/')
        else:
            messages.error(request, 'Something went wrong')
            return redirect('/admin/')
    else:
        if employee_status.active:
            employee_status.active = False
            employee_status.save()
        else:
            employee_status.active = True
            employee_status.save()

        messages.success(request, 'Your status has been change successfully')
        return redirect('/admin/')


@require_http_methods(['POST'])
@not_for_management
def change_project(request, *args, **kwargs):
    employee_project = EmployeeProject.objects.get(employee=request.user.employee)
    form = EmployeeProjectForm(request.POST, instance=employee_project)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your project has been changes successfully')
        return redirect('/admin/')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('/admin/')


@require_http_methods(['GET', 'POST',])
@login_required(login_url='/admin/login/')
@not_for_management
def employee_feedback(request, *args, **kwargs):
    if request.method == 'POST':
        form = EmployeeFeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your feedback has been submitted successfully')
            return redirect('/admin/')
        else:
            messages.error(request, 'Something went wrong')
            return redirect('/admin/')
    elif request.method == 'GET':

        this_month = datetime.datetime.today().replace(day=1)

        feedback = EmployeeFeedback.objects.filter(
            employee=request.user.employee, 
            created_at__gte=this_month
        ).first()

        form = EmployeeFeedbackForm(instance=feedback)

        context = {
            'employee_feedback_form': form,
        }
        
        return render(request, 'admin/form/employee_feedback_form.html', context)
