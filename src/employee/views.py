import json

from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from employee.forms.employee_online import EmployeeStatusForm
from employee.models import EmployeeActivity, EmployeeOnline


@require_http_methods(['POST'])
def change_status(request, *args, **kwargs):
    if get_client_id(request) in ['103.180.244.213', '127.0.0.1', '134.209.155.127']:
        employee_status = EmployeeOnline.objects.get(employee=request.user.employee)
        form = EmployeeStatusForm(request.POST, instance=employee_status)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your status has been change successfully')
            return redirect('/admin/')
        else:
            messages.error(request, 'Something went wrong')
            return redirect('/admin/')
    else:
        messages.error(request, 'You cannot change your activity status from out site office')
        return redirect('/admin/')


def get_client_id(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
