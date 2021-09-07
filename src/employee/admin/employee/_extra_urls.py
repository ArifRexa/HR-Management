import datetime

from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet, Sum, Value
from django import forms
from django.db.models.functions import Coalesce
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from account.models import EmployeeSalary
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
            path('<int:employee_id__exact>/salary/received-history/',
                 self.admin_site.admin_view(self.salary_receive_history), name='employee.salary.receive.history')
        ]
        return employee_urls + urls

    def salary_receive_history(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.employee.id != kwargs.get(*kwargs):
            raise PermissionDenied

        employee = Employee.objects.get(id=kwargs.get(*kwargs))
        employee_salaries = employee.employeesalary_set.filter(employee_id__exact=kwargs.get(*kwargs)).order_by('-id')
        context = dict(
            self.admin_site.each_context(request),
            employee=employee,
            employee_salaries=employee_salaries
        )
        return TemplateResponse(request, "admin/employee/paid_salary_history.html", context=context)

    def formal_summery(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        nearby_summery = EmployeeNearbySummery()
        context = dict(
            self.admin_site.each_context(request),
            title='Employee Calender',
            birthday=nearby_summery.birthdays(),
            permanent=nearby_summery.permanents,
            increment=nearby_summery.increments(),
            anniversaries=nearby_summery.anniversaries()
        )
        return TemplateResponse(request, "admin/employee/formal_summery.html", context=context)

    def hour_graph_view(self, request, *args, **kwargs):
        """
        Hour graph by employee id
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
        if not request.user.is_superuser and request.user.employee.id != kwargs.get(*kwargs):
            raise PermissionDenied
        print(request.GET)
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
            employee_hours = employee.employeeprojecthour_set.order_by('project_hour__date').filter(
                project_hour__date__gte=date_to_check).values(
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
                'data': data,
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


class EmployeeNearbySummery:
    """
    Employee nearby summery class
    will return birthdays, permanents, and employee to have an increment nearby
    """

    def __init__(self):
        self.today = datetime.datetime.today()
        self.employees = Employee.objects.filter(active=True)

    def birthdays(self):
        return self.employees.extra(
            select={'birth_month': 'month(date_of_birth)', 'birth_day': 'day(date_of_birth)'}).filter(
            date_of_birth__month__gte=timezone.now().date().month,
            date_of_birth__month__lte=(datetime.datetime.now() + datetime.timedelta(days=30)).month
        ).order_by('birth_month', 'birth_day')

    def permanents(self):
        return self.employees.filter(
            permanent_date__isnull=True,
            active=True,
            joining_date__lte=(datetime.date.today() - datetime.timedelta(days=80))
        ).order_by('joining_date')

    def increments(self):
        increment_employee = []
        for inc_employee in self.employees.all():
            if inc_employee.salaryhistory_set.count() > 0 and inc_employee.current_salary.active_from <= (
                    self.today - datetime.timedelta(days=150)).date():
                increment_employee.append(inc_employee)
        return increment_employee

    def anniversaries(self):
        return self.employees.filter(
            joining_date__month__in=[self.today.month, self.today.month + 1],
            permanent_date__isnull=False
        )
