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

from employee.models import Employee
from project_management.models import EmployeeProjectHour, ProjectHour, Project


class FilterForm(forms.Form):
    project_hour__date__gte = forms.DateField(label='', widget=AdminDateWidget(attrs={'readonly': 'readonly'}))
    project_hour__date__lte = forms.DateField(label=' ', widget=AdminDateWidget(attrs={'readonly': 'readonly'}))


class EmployeeExtraUrls(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        employee_urls = [
            path('graph/', self.admin_site.admin_view(self.all_employee_hour_graph_view)),
            path('<int:employee_id__exact>/graph/', self.admin_site.admin_view(self.hour_graph_view),
                 name='hour_graph'),
        ]
        return employee_urls + urls

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
        if not request.user.is_superuser:
            raise PermissionDenied
        print(request.GET.getlist('id__in[]'))
        employee_filter = {
            'active': True,
            'manager': False,
            'user__is_superuser': False
        }
        if len(request.GET.getlist('id__in[]')) > 0:
            employee_filter['id__in'] = request.GET.getlist('id__in[]')
        employees = Employee.objects.filter(**employee_filter).all()
        dataset = self._get_all_employee_dataset(employees)
        filter_form = FilterForm(initial={
            'project_hour__date__gte': request.GET.get('project_hour__date__gte', ''),
            'project_hour__date__lte': request.GET.get('project_hour__date__lte', '')
        })
        context = dict(
            self.admin_site.each_context(request),
            employees=employees,
            employees_array=list(employees.values_list('full_name', flat=True)),
            dataset=dataset,
            filter_form=filter_form,
        )
        return TemplateResponse(request, "admin/employee/all_employee_hour_graph.html", context)

    def _get_all_employee_dataset(self, employees):
        """

        @param employees:
        @return:
        """
        dataset = []
        for project in Project.objects.filter(active=True).all():
            color = f'rgb{(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))}'
            project_hour = {
                'label': project.title,
                'backgroundColor': color,
                'borderColor': color,
                'data': self._get_employee_project_hour(project, employees)
            }
            dataset.append(project_hour)
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
