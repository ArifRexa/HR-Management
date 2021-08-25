import datetime
import operator
import random
import re

from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet, Sum, Value
from django import forms
from django.db.models.functions import Coalesce
from django.forms import SelectDateWidget
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from rest_framework.fields import FloatField

from employee.models import Employee, SalaryHistory
from project_management.models import EmployeeProjectHour, ProjectHour, Project


class FilterForm(forms.Form):
    project_hour__date__gte = forms.DateField(label='', widget=AdminDateWidget(attrs={'readonly': 'readonly'}))
    project_hour__date__lte = forms.DateField(label=' ', widget=AdminDateWidget(attrs={'readonly': 'readonly'}))


class EmployeeExtraUrls(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        employee_urls = [
            path('formal-summery/', self.admin_site.admin_view(self.formal_summery), name='employee.summery'),
            path('graph/', self.admin_site.admin_view(self.all_employee_hour_graph_view), name='employee.hours.graph'),
            path('<int:employee_id__exact>/graph/', self.admin_site.admin_view(self.hour_graph_view),
                 name='hour_graph'),
        ]
        return employee_urls + urls

    def formal_summery(self, request, *args, **kwargs):
        employees = Employee.objects.filter(active=True)
        increment_employee = []
        today = datetime.datetime.today()
        for inc_employee in employees.all():
            if inc_employee.salaryhistory_set.count() > 0 and inc_employee.current_salary.active_from <= (
                    today - datetime.timedelta(days=150)).date():
                increment_employee.append(inc_employee)

        context = dict(
            self.admin_site.each_context(request),
            title='Employee Calender',
            birthday=employees.extra(
                select={'birth_month': 'month(date_of_birth)', 'birth_day': 'day(date_of_birth)'}).filter(
                date_of_birth__month__gte=timezone.now().date().month,
                date_of_birth__month__lte=(datetime.datetime.now() + datetime.timedelta(
                    days=30)).month).order_by('birth_month', 'birth_day'),
            permanent=employees.filter(permanent_date__isnull=True,
                                       active=True,
                                       joining_date__lte=(datetime.date.today() - datetime.timedelta(
                                           days=80))).order_by('joining_date'),
            increment=increment_employee,
            anniversaries=employees.filter(joining_date__month__in=[today.month, today.month + 1],
                                           permanent_date__isnull=False)
        )
        print(context['increment'])
        return TemplateResponse(request, "admin/employee/formal_summery.html", context=context)

    def hour_graph_view(self, request, *args, **kwargs):
        """

        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        filter_form = FilterForm(initial={
            'project_hour__date__gte': request.GET.get('project_hour__date__gte', ''),
            'project_hour__date__lte': request.GET.get('project_hour__date__lte', '')
        })
        context = dict(
            self.admin_site.each_context(request),
            chart=self._get_chart_data(request, *args, **kwargs),
            filter_form=filter_form,
            title=Employee.objects.get(pk=kwargs.get(*kwargs))
        )
        return TemplateResponse(request, "admin/employee/hour_graph.html", context)

    def _get_chart_data(self, request, *args, **kwargs):
        """

        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        chart = {'label': "Weekly View", 'total_hour': 0,
                 'labels': [], 'data': [], }

        filters = dict([(key, request.GET.get(key)) for key in dict(request.GET) if
                        key not in ['p', 'q', 'o', '_changelist_filters']])
        filters['employee_id__exact'] = kwargs.get(*kwargs)
        employee_hours = EmployeeProjectHour.objects.values('project_hour__date').filter(**filters).annotate(
            hours=Sum('hours'))
        for employee_hour in employee_hours:
            chart.get('labels').append(employee_hour['project_hour__date'].strftime('%B %d %Y'))
            chart.get('data').append(employee_hour['hours'])
            chart['total_hour'] += employee_hour['hours']

        return chart

    def all_employee_hour_graph_view(self, request):
        """

        @param request:
        @return:
        """
        context = dict(
            self.admin_site.each_context(request),
            series=self._get_all_employee_dataset()
        )
        return TemplateResponse(request, "admin/employee/all_employee_hour_graph.html", context)

    def _get_all_employee_dataset(self):
        """

        @param employees:
        @return:
        """
        dataset = []
        employees = Employee.objects.filter(active=True, manager=False).all()
        date_to_check = datetime.date.today() - datetime.timedelta(days=60)
        for employee in employees:
            data = []
            employee_hours = employee.employeeprojecthour_set.order_by('project_hour__date').values(
                'hours',
                'project_hour',
                'project_hour__date'
            )
            for employee_hour in employee_hours:
                timestamp = int(datetime.datetime.combine(
                    employee_hour['project_hour__date'],
                    datetime.datetime.min.time()
                ).timestamp())
                data.append([timestamp * 1000, employee_hour['hours']])
            dataset.append({
                'type': 'spline',
                'name': employee.full_name,
                'data': data
            })
        return dataset

    def _get_employee_project_hour(self, project, employees):
        """

        @param project:
        @param employees:
        @return:
        """
        employee_hours = []
        for employee in employees:
            total_hour = employee.employeeprojecthour_set.filter(project_hour__project=project).aggregate(
                sum_hours=Coalesce(Sum('hours'), Value(0.0))
            )
            total_project_manage_hour = employee.projecthour_set.filter(project=project).aggregate(
                sum_hours=Coalesce(Sum('hours'), Value(0.0))
            )
            employee_hours.append(total_hour['sum_hours'] + total_project_manage_hour['sum_hours'])
        return employee_hours
