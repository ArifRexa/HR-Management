import datetime
from dateutil.relativedelta import relativedelta

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.template.response import TemplateResponse

from employee.admin.employee._forms import FilterForm
from employee.models import Employee
from project_management.models import DailyProjectUpdate, EmployeeProjectHour, ProjectHour


class GraphView(admin.ModelAdmin):

    def all_employee_graph_view(self, request, *args, **kwargs):
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

    def employee_graph_view(self, request, *args, **kwargs):
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
            title=Employee.objects.get(pk=kwargs.get('employee_id__exact'))
        )
        return TemplateResponse(request, "admin/employee/hour_graph.html", context)

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
            if employee_hours.count() > 0:
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

    def _get_chart_data(self, request, *args, **kwargs):
        """

        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        employee_id = kwargs.get('employee_id__exact')
        if not request.user.is_superuser and request.user.employee.id != employee_id:
            raise PermissionDenied
        chart = {'label': "Weekly View", 'total_hour': 0,
                 'labels': [], 'data': [], }

        filters = dict([(key, request.GET.get(key)) for key in dict(request.GET) if
                        key not in ['p', 'q', 'o', '_changelist_filters']])
        filters['employee_id__exact'] = employee_id
        employee_hours = EmployeeProjectHour.objects.values('project_hour__date').filter(**filters).annotate(
            hours=Sum('hours'))
        for employee_hour in employee_hours:
            chart.get('labels').append(employee_hour['project_hour__date'].strftime('%B %d %Y'))
            chart.get('data').append(employee_hour['hours'])
            chart['total_hour'] += employee_hour['hours']
        return chart
    
    def employee_time_base_graph_view(self, request, *args, **kwargs):
        """
        Hour graph by employee id
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        
        if  not request.user.has_perm("employee.view_employeeundertpm"):
            raise PermissionDenied("You do not have permission to access this feature.")
        filter_form = FilterForm(initial={
            'project_hour__date__gte': request.GET.get('project_hour__date__gte', ''),
            'project_hour__date__lte': request.GET.get('project_hour__date__lte', '')
        })
        context = dict(
            self.admin_site.each_context(request),
            chart=self._get_employee_chart_data_by_month_weekly_base(request, *args, **kwargs),
            filter_form=filter_form,
            title=Employee.objects.get(pk=kwargs.get('employee_id__exact'))
        )
        return TemplateResponse(request, "admin/employee/time_base_hour_graph.html", context)

    def _get_employee_chart_data_by_month_weekly_base(self, request, *args, **kwargs):
        """
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        employee_id = kwargs.get('employee_id__exact')
        if not request.user.is_superuser and request.user.employee.id != employee_id:
            raise PermissionDenied
        chart = {
            "weekly": {
                "label": "Weekly View",
                "total_hour": 0,
                "labels": [],
                "data": [],
            },
            "monthly": {
                "label": "Monthly View",
                "total_hour": 0,
                "labels": [],
                "data": [],
            },
            "daily": {
                "label": "Daily View",
                "total_hour": 0,
                "labels": [],
                "data": [],
            },
        }

        filters = dict([(key, request.GET.get(key)) for key in dict(request.GET) if
                        key not in ['p', 'q', 'o', '_changelist_filters']])
        filters['employee_id__exact'] = employee_id

        filtered_employee_hours = EmployeeProjectHour.objects.filter(
            **filters,
        )
        
        employee_monthly_hours = filtered_employee_hours.annotate(
            month=TruncMonth("created_at__date")
        ).values("month").annotate(
            monthly_hour = Sum("hours")
        ).order_by("month")
        for employee_monthly_hour in employee_monthly_hours:
            chart["monthly"]["labels"].append(employee_monthly_hour.get("month").strftime("%d-%b-%Y"))
            chart["monthly"]["data"].append(employee_monthly_hour.get("monthly_hour"))
            chart["monthly"]["total_hour"] += employee_monthly_hour.get("monthly_hour")

        weekly_employee_hours = EmployeeProjectHour.objects.values(
            "project_hour__date"
        ).filter(**filters).annotate(
            hours=Sum("hours")
        ).order_by("project_hour__date")

        for weekly_employee_hour in weekly_employee_hours:
            chart["weekly"]["labels"].append(weekly_employee_hour.get("project_hour__date").strftime("%d-%b-%Y"))
            chart["weekly"]["data"].append(weekly_employee_hour.get("hours"))
            chart["weekly"]["total_hour"] += weekly_employee_hour.get("hours")
        

        start_date = datetime.date.today() - relativedelta(months=6)
        daily_employee_hours = DailyProjectUpdate.objects.filter(
            created_at__date__gte=start_date,
            status="approved",
            **filters,
        ).values(
            "created_at__date",
        ).annotate(
            total_hour = Sum("hours")
        ).order_by("created_at__date")

        for daily_employee_hour in daily_employee_hours:
            chart["daily"]["labels"].append(daily_employee_hour.get("created_at__date").strftime("%d-%b-%Y"))
            chart["daily"]["data"].append(daily_employee_hour.get("total_hour"))
            chart["daily"]["total_hour"] += daily_employee_hour.get("total_hour")
        return chart
    
    def project_graph_view(self, request, *args, **kwargs):
        """
        Hour graph by project id
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
            title=ProjectHour.objects.get(pk=kwargs.get('project_id__exact'))
        )
        return TemplateResponse(request, "admin/employee/hour_graph.html", context)
    
    
    def _get_project_chart_data_by_month_weekly_base(self, request, *args, **kwargs):
        """
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        project_id = kwargs.get('project_id__exact')
        if not request.user.is_superuser:
            raise PermissionDenied
        chart = {
            "weekly": {
                "label": "Weekly View",
                "total_hour": 0,
                "labels": [],
                "data": [],
            },
            "monthly": {
                "label": "Monthly View",
                "total_hour": 0,
                "labels": [],
                "data": [],
            },
        }
        employee_id = 1
        filters = dict([(key, request.GET.get(key)) for key in dict(request.GET) if
                        key not in ['p', 'q', 'o', '_changelist_filters']])
        filters['employee_id__exact'] = employee_id

        filtered_employee_hours = EmployeeProjectHour.objects.filter(
            **filters,
        )
        
        employee_monthly_hours = filtered_employee_hours.annotate(
            month=TruncMonth("created_at__date")
        ).values("month").annotate(
            monthly_hour = Sum("hours")
        ).order_by("month")
        for employee_monthly_hour in employee_monthly_hours:
            chart["monthly"]["labels"].append(employee_monthly_hour.get("month").strftime("%d-%b-%Y"))
            chart["monthly"]["data"].append(employee_monthly_hour.get("monthly_hour"))
            chart["monthly"]["total_hour"] += employee_monthly_hour.get("monthly_hour")

        weekly_employee_hours = EmployeeProjectHour.objects.values(
            "project_hour__date"
        ).filter(**filters).annotate(
            hours=Sum("hours")
        ).order_by("project_hour__date")

        for weekly_employee_hour in weekly_employee_hours:
            chart["weekly"]["labels"].append(weekly_employee_hour.get("project_hour__date").strftime("%d-%b-%Y"))
            chart["weekly"]["data"].append(weekly_employee_hour.get("hours"))
            chart["weekly"]["total_hour"] += weekly_employee_hour.get("hours")
        return chart
    