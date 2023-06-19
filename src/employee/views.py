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
import datetime
from employee.models import Config
from employee.mail import cto_help_mail, hr_help_mail

@white_listed_ip_check
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

    if not feedback.exists() and now.day > 20:
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
        employee.need_cto_at = None
        employee.save()
        messages.success(request, 'I got help from Tech Lead. Thank You.')
        return redirect('/admin/')
    else:
        employee.need_cto = True
        employee.need_cto_at = timezone.now()
        employee.save()

        today = datetime.date.today()
        dayname = today.strftime("%A")
        off_list = ["Saturday", "Sunday"]

        if not dayname in off_list:
            print('send email')
            if Config.objects.first().cto_email is not None:
                email_list = Config.objects.first().cto_email.strip()
                email_list = email_list.split(',')
                cto_help_mail(request.user.employee, {'waitting_at': timezone.now(), 'receiver' : email_list})

        messages.success(request, 'Your request has successfully submited. Tech Lead will contact with you.')
        return redirect('/admin/')



@require_http_methods(['POST', 'GET'])
@login_required(login_url='/admin/login/')
@not_for_management
def need_hr_help(request, *args, **kwargs):
    employee = Employee.objects.get(id=request.user.employee.id)
    if request.user.employee.need_hr:
        employee.need_hr = False
        employee.need_hr_at = None
        employee.save()
        messages.success(request, 'Got help from HR. Thank You.')
        return redirect('/admin/')
    else:
        employee.need_hr = True
        employee.need_hr_at = timezone.now()
        employee.save()

        today = datetime.date.today()
        dayname = today.strftime("%A")
        off_list = ["Saturday", "Sunday"]

        if not dayname in off_list:
            if Config.objects.first().hr_email is not None:
                email_list = Config.objects.first().hr_email.strip()
                email_list = email_list.split(',')
                hr_help_mail(
                    request.user.employee, 
                    {
                        'waiting_at': timezone.now(), 
                        'receiver' : email_list
                    },
                )

        messages.success(request, 'Your request has successfully submited. HR will contact with you.')
        return redirect('/admin/')



from rest_framework import serializers
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated

from employee.models.employee import Task

class TodoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"


class TodoApiList(ListAPIView):
    serializer_class = TodoSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)
    
class TodoCreateAPI(CreateAPIView):
    serializer_class = TodoSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

class TodoRetriveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)