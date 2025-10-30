import calendar
import datetime

from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import F, Sum
from django.db.models.functions import TruncMonth, TruncYear
from django.template.response import TemplateResponse

from employee.admin.employee._forms import (
    DateFilterForm, FilterForm,
    DailyUpdateDateFilterForm,
    ClientProjectsHourFilterForm,
)
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
        return TemplateResponse(request, "admin/employee/employee_time_base_hour_graph.html", context)

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
            "employee_id": employee_id,
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
            month=TruncMonth("project_hour__date"),
        ).values("month").annotate(
            monthly_hour = Sum("hours")
        ).order_by("month")

        employee_hours = EmployeeProjectHour.objects.select_related(
            "project_hour",
            "project_hour__project",
        ).filter(
            **filters
        ).only(
            "project_hour__date",
            "project_hour__project__title",
            "hours",
        ).order_by("project_hour__date")

        projects_hour_by_date = dict()
        for employee_hour in employee_hours:
            date = employee_hour.project_hour.date.strftime("%b-%Y")
            item = projects_hour_by_date.get(date, [])
            if item:
                item.append([employee_hour.project_hour.project.title, employee_hour.hours])
            else:
                projects_hour_by_date[date] = [[employee_hour.project_hour.project.title, employee_hour.hours]]
        for employee_monthly_hour in employee_monthly_hours:
            date = employee_monthly_hour.get("month")
            chart["monthly"]["labels"].append(date.strftime("%b-%Y"))
            chart["monthly"]["data"].append(employee_monthly_hour.get("monthly_hour"))
            chart["monthly"]["total_hour"] += employee_monthly_hour.get("monthly_hour")
            employee_hour_list = EmployeeProjectHour.objects.filter(
                employee_id=filters.get("employee_id__exact"),
                project_hour__date__month=date.month,
                project_hour__date__year=date.year,
            ).values('id', "project_hour__date", "project_hour__project__title", "hours")
            chart["monthly"]["per_day_count"].append(
                {
                    "project_by_project_hour": projects_hour_by_date.get(date.strftime("%b-%Y"), []),
                    "all_project_hour": list([
                        {
                            'id': a.get('id'),
                            "date": a.get("project_hour__date").strftime("%d-%b-%Y"),
                            "name": a.get("project_hour__project__title"),
                            "hour": a.get("hours"),
                        }
                        for a in employee_hour_list
                    ]),
                }
            )
        
        if request.GET.get('project_hour__date__gte') is None:
            filters["project_hour__date__gte"] = filters["project_hour__date__gte"] + relativedelta(months=6)

        weekly_employee_hours = EmployeeProjectHour.objects.values(
            "project_hour__date"
        ).filter(**filters).annotate(
            t_hours=Sum("hours"),
        ).order_by("project_hour__date")

        employee_hours = EmployeeProjectHour.objects.select_related(
            "project_hour",
            "project_hour__project",
        ).filter(
            **filters
        ).only(
            "project_hour__date",
            "project_hour__project__title",
            "hours",
        ).order_by("project_hour__date")

        projects_hour_by_date = dict()
        for employee_hour in employee_hours:
            date = employee_hour.project_hour.date.strftime("%d-%b-%Y")
            item = projects_hour_by_date.get(date, [])
            if item:
                item.append([employee_hour.project_hour.project.title, employee_hour.hours])
            else:
                projects_hour_by_date[date] = [[employee_hour.project_hour.project.title, employee_hour.hours]]

        employee_hour = EmployeeProjectHour.objects.filter(
            **filters
        )
        for weekly_employee_hour in weekly_employee_hours:
            date = weekly_employee_hour.get("project_hour__date").strftime("%d-%b-%Y")
            chart["weekly"]["labels"].append(date)
            chart["weekly"]["data"].append(weekly_employee_hour.get("t_hours"))
            
            employee_hour_list = employee_hour.filter(
                project_hour__date=weekly_employee_hour.get("project_hour__date")
            ).values_list("hours", flat=True)
            chart["weekly"]["per_day_count"].append(
                {
                    "project_by_project_hour": projects_hour_by_date.get(date, []),
                    "all_project_hour": list(employee_hour_list),
                }
            )
            chart["weekly"]["total_hour"] += weekly_employee_hour.get("t_hours")        

        """
        for daily update
        """
        
        filters["created_at__date__lte"] = filters.pop("project_hour__date__lte")
        filters["created_at__date__gte"] = filters.pop("project_hour__date__gte")
        if request.GET.get('project_hour__date__gte') is None:
            filters["created_at__date__gte"] = filters["created_at__date__gte"] + relativedelta(months=5)
        # filters.pop("project_hour__date__gte")
        # filters.pop("project_hour__date__lte")
        # filters["created_at__date__gte"] = datetime.date.today() - relativedelta(days=30)
        # filters["created_at__date__lte"] = datetime.date.today()

        daily_employee_hours_filtered_queryset = DailyProjectUpdate.objects.filter(
            # status="approved",
            **filters,
        )
        daily_project_base_employee_hours = daily_employee_hours_filtered_queryset.select_related(
            "project",
        ).only(
            "project__title",
            "hours",
        ).order_by("created_at__date")
        daily_project_base_employee_hour_data = dict()
        for daily_project_base_employee_hour in daily_project_base_employee_hours:
            date = daily_project_base_employee_hour.created_at.strftime("%d-%b-%Y")
            project_title = daily_project_base_employee_hour.project.title
            project_hour = daily_project_base_employee_hour.hours
            old_data = daily_project_base_employee_hour_data.get(date)
            if old_data:
                old_data.append([project_title, project_hour])
            else:
                daily_project_base_employee_hour_data[date] = [[project_title, project_hour]]

        daily_employee_hours = daily_employee_hours_filtered_queryset.values(
            "created_at__date",
        ).annotate(
            total_hour = Sum("hours")
        ).order_by("created_at__date")

        for daily_employee_hour in daily_employee_hours:
            date = daily_employee_hour.get("created_at__date").strftime("%d-%b-%Y")
            chart["daily"]["labels"].append(date)
            chart["daily"]["data"].append(daily_employee_hour.get("total_hour"))
            chart["daily"]["total_hour"] += daily_employee_hour.get("total_hour")
            chart["daily"]["per_day_count"].append(daily_project_base_employee_hour_data.get(date, []))
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
        start_date = current_date - relativedelta(months=6)

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
        project_id = kwargs.get('project_id__exact')
        chart = {
            "project_id": project_id,
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
        filters["project_id__exact"] = project_id
        filtered_project_hours = ProjectHour.objects.filter(
            # status="approved",
            **filters,
        )
        
        weekly_project_hours = filtered_project_hours.values(
            "date",
        ).annotate(
            hours=Sum("hours"),
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
        current_date = datetime.date.today()
        start_date = current_date - relativedelta(years=1)
        initial_filter = {
            # "total_hour__gte" : request.GET.get("total_hour__gte"),
            # "total_hour__lte" : request.GET.get("total_hour__lte"),
            "date__gte" : request.GET.get("date__gte", start_date),
            "date__lte" : request.GET.get("date__lte", current_date),
        }
        filters = {key: value for key, value in initial_filter.items() if value}
        filter_form = ClientProjectsHourFilterForm(
            initial={**filters},
        )
        context = dict(
            self.admin_site.each_context(request),
            chart_data=self._get_client_all_projects_dataset(client_id=kwargs.get("client_id"), filters=filters),
            filter_form=filter_form,
        )
        return TemplateResponse(request, "admin/employee/client_projects_hour_graph.html", context)
    
    def _get_client_all_projects_dataset(self, client_id:int, filters:dict):
        projects = Project.objects.select_related("client").only("title", "client").filter(client_id=client_id)
        dataset = dict()
        client_name = projects.first().client.name
        date_filters = {
            "date__gte": filters.pop("date__gte")
        }
        if filters.get("date__lte"):
            date_filters["date__lte"] = filters.pop("date__lte")
        # for all project
        # weekly projects hours
        all_project_hours = ProjectHour.objects.filter(
            project_id__in=projects.values_list("id", flat=True),
            **date_filters,
        )
        if projects.count() > 1 and all_project_hours.exists():
            weekly_all_project_hours = all_project_hours.values("date").annotate(
                total_hour = Sum("hours")
            ).filter(
                **filters,
            ).order_by("date")
            chart = {
                "weekly": {
                    "label": "Weekly Hours",
                    "client_name": client_name,
                    "labels": [],
                    "data": [],
                    "total_hour": 0,
                },
                "monthly": {
                    "label": "Monthly Hours",
                    "client_name": client_name,
                    "labels": [],
                    "data": [],
                    "total_hour": 0,
                }
            }
            for weekly_project_hour in weekly_all_project_hours:
                chart["weekly"]["labels"].append(weekly_project_hour.get("date").strftime("%d-%b-%Y"))
                chart["weekly"]["data"].append(weekly_project_hour.get("total_hour"))
                chart["weekly"]["total_hour"] += weekly_project_hour.get("total_hour")
            monthly_all_project_hours = all_project_hours.values(
                "date__year", "date__month"
            ).annotate(
                total_hour = Sum("hours"),
            ).filter(
                **filters,
            ).order_by("date__year", "date__month")
            for monthly_project_hour in monthly_all_project_hours:
                month_num = str(monthly_project_hour.get("date__month")).zfill(2)
                month_abbr = calendar.month_abbr[int(month_num)]
                chart["monthly"]["labels"].append(f"{month_abbr}-{monthly_project_hour.get('date__year')}")
                chart["monthly"]["data"].append(monthly_project_hour.get("total_hour"))
                chart["monthly"]["total_hour"] += monthly_project_hour.get("total_hour")
            dataset["All Projects"] = {
                "name": "All Projects",
                **chart,
            }
        # for project by project
        for project in projects:
            project_hours = ProjectHour.objects.filter(
                project_id=project.id,
                **date_filters,
            )

            if project_hours.count() > 0:
                weekly_project_hours = project_hours.values("date").annotate(
                    total_hour = Sum("hours")
                ).filter(
                    **filters,
                ).order_by("date")
                chart = {
                    "weekly": {
                        "label": "Weekly Hours",
                        "client_name": client_name,
                        "labels": [],
                        "data": [],
                        "total_hour": 0,
                    },
                    "monthly": {
                        "label": "Monthly Hours",
                        "client_name": client_name,
                        "labels": [],
                        "data": [],
                        "total_hour": 0,
                    }
                }
                for project_hour in weekly_project_hours:
                    chart["weekly"]["labels"].append(project_hour.get("date").strftime("%d-%b-%Y"))
                    chart["weekly"]["data"].append(project_hour.get("total_hour"))
                    chart["weekly"]["total_hour"] += project_hour.get("total_hour")
                
                monthly_project_hours = project_hours.values(
                    "date__year", "date__month",
                ).annotate(
                    total_hour = Sum("hours"),
                ).filter(
                    **filters,
                ).order_by("date__year", "date__month",)
                for monthly_project_hour in monthly_project_hours:
                    month_num = str(monthly_project_hour.get("date__month")).zfill(2)
                    month_abbr = calendar.month_abbr[int(month_num)]
                    chart["monthly"]["labels"].append(f"{month_abbr}-{monthly_project_hour.get('date__year')}")
                    chart["monthly"]["data"].append(monthly_project_hour.get("total_hour"))
                    chart["monthly"]["total_hour"] += monthly_project_hour.get("total_hour")
                dataset[project.title] = {
                    "name": project.title,
                    **chart,
                }
        return dataset

    def all_employee_last_working_day_graph_view(self, request, *args, **kwargs):
        if request.user.has_perm("employee.view_employeeundertpm") is False:
            raise PermissionDenied("You do not have permission to access this feature.")
        
        if request.GET.get("created_at__date"):
            current_date = request.GET.get("created_at__date")
        else:
            current_date_time = datetime.datetime.now()
            current_date = current_date_time.date()
            weekday = current_date.weekday()
            if weekday in (5, 6):
                # get the last working date if current_date is Saturday or Sunday 
                current_date = current_date - relativedelta(days=1 if weekday == 5 else 2)
            elif current_date_time.time() < datetime.time(21, 0, 0):  # define 9 PM, time(21, 0, 0)
                # get the last working date if current_time is less then 9 PM
                days = 3 if weekday == 0 else 1
                current_date = current_date - relativedelta(days=days)

        hours_filters = {key: request.GET.get(key) for key in ["total_hour__gte", "total_hour__lte"] if request.GET.get(key)}
        initial_date_filter = {
            "created_at__date": current_date,
            **hours_filters,
        }
        date_filter_form = DailyUpdateDateFilterForm(
            initial=initial_date_filter,
        )
        context = dict(
            self.admin_site.each_context(request),
            chart=self._all_employee_last_working_day_graph_data(
                date_filters={"created_at__date": current_date},
                hours_filters=hours_filters,
            ),
            date_filter_form=date_filter_form,
        )
        return TemplateResponse(request, "admin/employee/employees_last_working_day_hours.html", context)

    def _all_employee_last_working_day_graph_data(self, date_filters, hours_filters):
        daily_employee_hours = (
            DailyProjectUpdate.objects.filter(**date_filters)
            .select_related("employee", "project")
            .values("employee", "employee__full_name")
            .annotate(total_hour=Sum("hours")).filter(**hours_filters)
            .order_by("total_hour")
        )

        project_data = (
            DailyProjectUpdate.objects.filter(**date_filters)
            .select_related("project")
            .values("employee", "project__title", "hours")
            .order_by("employee", "project__title")
        )

        employee_projects = {}
        for entry in project_data:
            employee_id = entry["employee"]
            if employee_id not in employee_projects:
                employee_projects[employee_id] = []
            employee_projects[employee_id].append([entry["project__title"], entry["hours"]])

        chart = {
            "label": "Daily Project Hours",
            "labels": [],
            "data": [],
            "projects_hour": [],
            "employees_id": [],
            "total_hour": 0,
        }
        for daily_employee_hour in daily_employee_hours:
            employee_id = daily_employee_hour["employee"]
            chart["labels"].append(daily_employee_hour["employee__full_name"])
            chart["data"].append(daily_employee_hour["total_hour"])
            chart["employees_id"].append(employee_id)
            chart["projects_hour"].append(employee_projects.get(employee_id, []))
            chart["total_hour"] += daily_employee_hour["total_hour"]
        return chart

