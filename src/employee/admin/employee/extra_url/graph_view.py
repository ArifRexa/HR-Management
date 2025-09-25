import calendar
import datetime

from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import F, Sum
from django.db.models.functions import TruncMonth
from django.template.response import TemplateResponse

from employee.admin.employee._forms import DateFilterForm, FilterForm
from employee.models import Employee
from project_management.models import (
    DailyProjectUpdate,
    EmployeeProjectHour,
    Project,
    ProjectHour,
)


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
        current_date = datetime.date.today()
        start_date = current_date - relativedelta(months=6)
        u = request.user.employee.id != kwargs.get('employee_id__exact')
        p = request.user.has_perm("employee.view_employeeundertpm") is False
        if request.user.has_perm("employee.view_employeeundertpm") is False and request.user.employee.id != kwargs.get('employee_id__exact'):
            raise PermissionDenied("You do not have permission to access this feature.")
        
        initial_filter = {
            'project_hour__date__gte': request.GET.get('project_hour__date__gte', start_date),
            'project_hour__date__lte': request.GET.get('project_hour__date__lte', current_date),
        }
        filter_form = FilterForm(initial={**initial_filter})
        context = dict(
            self.admin_site.each_context(request),
            chart=self._get_employee_chart_data_by_daily_month_weekly_base(
                request,
                *args,
                apply_filter=initial_filter,
                **kwargs,
            ),
            filter_form=filter_form,
            title=Employee.objects.get(pk=kwargs.get('employee_id__exact'))
        )
        return TemplateResponse(request, "admin/employee/time_base_hour_graph.html", context)

    def _get_employee_chart_data_by_daily_month_weekly_base(self, request, *args, **kwargs):
        """
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        employee_id = kwargs.get('employee_id__exact')
        if not request.user.is_superuser and request.user.has_perm("employee.view_employeeundertpm") is False and request.user.employee.id != kwargs.get('employee_id__exact'):
            raise PermissionDenied
        employee_monthly_expected_hour = Employee.objects.only(
            "monthly_expected_hours"
        ).get(id=employee_id).monthly_expected_hours

        chart = {
            "daily": {
                "label": "Daily Hours",
                "total_hour": 0,
                "target_hour": round(float(employee_monthly_expected_hour or 0)/20, 2),
                "labels": [],
                "data": [],
                "per_day_count": [],
            },
            "weekly": {
                "label": "Weekly Hours",
                "total_hour": 0,
                "target_hour": round(float(employee_monthly_expected_hour or 0)/4, 2),
                "labels": [],
                "data": [],
                "per_day_count": [],
            },
            "monthly": {
                "label": "Monthly Hours",
                "total_hour": 0,
                "target_hour": round(float(employee_monthly_expected_hour or 0), 2),
                "labels": [],
                "data": [],
                "per_day_count": [],
            },
        }

        filters = kwargs.get("apply_filter")
        filters['employee_id__exact'] = employee_id
        if request.GET.get('project_hour__date__gte') is None:
            filters["project_hour__date__gte"] = filters["project_hour__date__gte"] - relativedelta(months=6)
        
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
        
        if request.GET.get('project_hour__date__gte') is None:
            filters["project_hour__date__gte"] = filters["project_hour__date__gte"] + relativedelta(months=6)

        weekly_employee_hours = EmployeeProjectHour.objects.values(
            "project_hour__date"
        ).filter(**filters).annotate(
            t_hours=Sum("hours"),
        ).order_by("project_hour__date")
        employee_hour = EmployeeProjectHour.objects.filter(
            **filters
        )
        for weekly_employee_hour in weekly_employee_hours:
            chart["weekly"]["labels"].append(weekly_employee_hour.get("project_hour__date").strftime("%d-%b-%Y"))
            chart["weekly"]["data"].append(weekly_employee_hour.get("t_hours"))
            employee_hour_list = employee_hour.filter(
                project_hour__date=weekly_employee_hour.get("project_hour__date")
            ).values_list("hours", flat=True)
            chart["weekly"]["per_day_count"].append(list(employee_hour_list))
            chart["weekly"]["total_hour"] += weekly_employee_hour.get("t_hours")        

        filters["created_at__date__gte"] = filters.pop("project_hour__date__gte")
        filters["created_at__date__lte"] = filters.pop("project_hour__date__lte")
        daily_employee_hours = DailyProjectUpdate.objects.filter(
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
        if request.user.has_perm("employee.view_employeeundertpm") is False:
            raise PermissionDenied("You do not have permission to access this feature.")
        
        current_date = datetime.date.today()
        start_date = current_date - relativedelta(years=1)

        initial_filter = {
            'date__gte': request.GET.get('date__gte', start_date),
            'date__lte': request.GET.get('date__lte', current_date),
        }

        filter_form = DateFilterForm(initial={**initial_filter})
        context = dict(
            self.admin_site.each_context(request),
            chart=self._get_project_chart_data_by_month_weekly_base(request, *args, filters=initial_filter, **kwargs),
            filter_form=filter_form,
            title=Project.objects.only("title").get(pk=kwargs.get('project_id__exact')).title
        )
        return TemplateResponse(request, "admin/employee/time_base_project_hour_graph.html", context)

    def _get_project_chart_data_by_month_weekly_base(self, request, *args, **kwargs):
        """
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        chart = {
            "weekly": {
                "label": "Weekly Hours",
                "total_hour": 0,
                "labels": [],
                "data": [],
            },
            "monthly": {
                "label": "Monthly Hours",
                "total_hour": 0,
                "labels": [],
                "data": [],
            },
        }
        
        filters = kwargs.get("filters")
        filters["project_id__exact"] = kwargs.get('project_id__exact')
        filtered_project_hours = ProjectHour.objects.filter(
            status="approved",
            **filters,
        )
        
        weekly_project_hours = filtered_project_hours.values(
            "date",
        ).annotate(
            hours=F("hours"),
        ).order_by("date")

        for weekly_project_hour in weekly_project_hours:
            chart["weekly"]["labels"].append(weekly_project_hour.get("date").strftime("%d-%b-%Y"))
            hour = weekly_project_hour.get("hours")
            chart["weekly"]["data"].append(hour)
            chart["weekly"]["total_hour"] += hour

        monthly_project_hours = filtered_project_hours.values(
            "date__month",
            "date__year",
        ).annotate(
            total_hour = Sum("hours"),
        ).order_by("date__year", "date__month")

        for monthly_project_hour in monthly_project_hours:
            month_num = str(monthly_project_hour.get("date__month")).zfill(2)
            month_abbr = calendar.month_abbr[int(month_num)]
            chart["monthly"]["labels"].append(f"{month_abbr}-{monthly_project_hour.get('date__year')}")
            hour = monthly_project_hour.get("total_hour")
            chart["monthly"]["data"].append(hour)
            chart["monthly"]["total_hour"] += hour
        return chart

    def clinet_projects_graph(self, request, *args, **kwargs):
        if request.user.has_perm("employee.view_employeeundertpm") is False:
            raise PermissionDenied("You do not have permission to access this feature.")

        context = dict(
            self.admin_site.each_context(request),
            series=self._get_client_all_projects_dataset(client_id=kwargs.get("client_id")),
        )
        return TemplateResponse(request, "admin/employee/client_projects_hour_graph.html", context)
    
    def _get_client_all_projects_dataset(self, client_id):
        dataset = []
        start_date = datetime.date.today() - relativedelta(years=1)
        projects = Project.objects.only("title").filter(client_id=client_id)

        # for all project
        all_project_hours = ProjectHour.objects.filter(
            date__gte=start_date,
            project_id__in=projects.values_list("id", flat=True),
        ).values("date").annotate(
            total_hour = Sum("hours")
        ).order_by("date")
        if all_project_hours.exists():
            data = []
            for project_hour in all_project_hours:
                timestamp = int(
                    datetime.datetime.combine(
                        project_hour.get("date"),
                        datetime.datetime.min.time()
                    ).timestamp()
                )
                data.append([timestamp * 1000, project_hour.get("total_hour")])
            dataset.append(
                {
                    "type": "spline",
                    "name": "All Projects",
                    "data": data,
                }
            )
        
        # for project by project
        for project in projects:
            project_hours = ProjectHour.objects.filter(
                date__gte=start_date,
                project_id=project.id
            ).values("date").annotate(
                total_hour = Sum("hours")
            ).order_by("date")

            if project_hours.count() > 0:
                data = []
                for project_hour in project_hours:
                    timestamp = int(
                        datetime.datetime.combine(
                            project_hour.get("date"),
                            datetime.datetime.min.time()
                        ).timestamp()
                    )
                    data.append([timestamp * 1000, project_hour.get("total_hour")])
                dataset.append(
                    {
                        "type": "spline",
                        "name": project.title,
                        "data": data,
                    }
                )
        return dataset
