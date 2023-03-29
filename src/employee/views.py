import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from employee.forms.employee_online import EmployeeStatusForm
from employee.forms.employee_project import EmployeeProjectForm
from employee.models import EmployeeActivity, EmployeeOnline, Employee
from employee.models.employee_activity import EmployeeProject
from config.admin.utils import white_listed_ip_check, not_for_management
from config.settings import employee_ids as management_ids
# white_listed_ips = ['103.180.244.213', '127.0.0.1', '134.209.155.127', '45.248.149.252']
from django.http import HttpResponse

# @white_listed_ip_check
@require_http_methods(['POST', 'GET'])
@login_required(login_url='/admin/login/')
@not_for_management
def change_status(request, *args, **kwargs):
    employee_status = EmployeeOnline.objects.get(employee=request.user.employee)

    now = timezone.now().date()

    feedback = request.user.employee.employeefeedback_set.filter(
        created_at__date__year=now.year,
        created_at__date__month=now.month,
    )
    # TODO : feedback should not be applied for Himel vai

    if not feedback.exists() and now.day > 25:
        messages.error(request, 'Please provide feedback first')
        return redirect('/admin/')

    if request.method == 'POST':
        form = EmployeeStatusForm(request.POST, instance=employee_status)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your status has been change successfully')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Something went wrong')
            return redirect(request.META.get('HTTP_REFERER'))
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
@login_required(login_url='/admin/login/')
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


@require_http_methods(['POST', 'GET'])
@login_required(login_url='/admin/login/')
@not_for_management
def need_cto_help(request, *args, **kwargs):
    employee = Employee.objects.get(id=request.user.employee.id)
    if request.user.employee.need_cto:
        employee.need_cto = False
        employee.save()
        messages.success(request, 'I got help from CTO. Thank You.')
        return redirect('/admin/')
    else:
        employee.need_cto = True
        employee.save()

        messages.success(request, 'Your request has successfully submited. CTO will contact with you.')
        return redirect('/admin/')


