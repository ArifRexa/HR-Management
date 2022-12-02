import json

from django.http import JsonResponse

# Create your views here.
from django.shortcuts import redirect

from employee.forms.employee_online import EmployeeStatusForm
from employee.models import EmployeeActivity, EmployeeOnline


def change_status(request, *args, **kwargs):
    if request.method == 'POST':
        employee_status = EmployeeOnline.objects.get(employee=request.user.employee)
        form = EmployeeStatusForm(request.POST, instance=employee_status)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('/admin/')
        else:
            return redirect('/wrong-page/')
