import re

from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.db.models import QuerySet, Sum
from django import forms
from django.forms import SelectDateWidget
from django.template.response import TemplateResponse
from django.urls import path

from employee.models import Employee
from project_management.models import EmployeeProjectHour, ProjectHour


class FilterForm(forms.Form):
    project_hour__date__gte = forms.DateField(label='', widget=AdminDateWidget())
    project_hour__date__lte = forms.DateField(label=' ', widget=AdminDateWidget())


class EmployeeExtraUrls(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        employee_urls = [
            path('<int:employee_id__exact>/graph/', self.admin_site.admin_view(self.hour_graph_view),
                 name='hour_graph'),
        ]
        return employee_urls + urls

    def hour_graph_view(self, request, *args, **kwargs):
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
