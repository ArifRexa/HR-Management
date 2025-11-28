import calendar
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.template.response import TemplateResponse
from django.utils import timezone

from employee.admin.employee._forms import (
    ClientProjectsHourFilterForm,
    DailyUpdateDateFilterForm,
    DateFilterForm,
    FilterForm,
)
from employee.models import Employee
from employee.models.employee_skill import Skill
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
            series=self._get_all_employee_dataset(),
        )
        return TemplateResponse(
            request, "admin/employee/all_employee_hour_graph.html", context
        )

    def employee_graph_view(self, request, *args, **kwargs):
        """
        Hour graph by employee id
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        filter_form = FilterForm(
            initial={
                "project_hour__date__gte": request.GET.get(
                    "project_hour__date__gte", ""
                ),
                "project_hour__date__lte": request.GET.get(
                    "project_hour__date__lte", ""
                ),
            }
        )
        context = dict(
            self.admin_site.each_context(request),
            chart=self._get_chart_data(request, *args, **kwargs),
            filter_form=filter_form,
            title=Employee.objects.get(pk=kwargs.get("employee_id__exact")),
        )
        return TemplateResponse(
            request, "admin/employee/hour_graph.html", context
        )

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
            employee_hours = (
                employee.employeeprojecthour_set.order_by("project_hour__date")
                .filter(project_hour__date__gte=date_to_check)
                .values("hours", "project_hour", "project_hour__date")
            )
            if employee_hours.count() > 0:
                for employee_hour in employee_hours:
                    timestamp = int(
                        datetime.datetime.combine(
                            employee_hour["project_hour__date"],
                            datetime.datetime.min.time(),
                        ).timestamp()
                    )
                    data.append([timestamp * 1000, employee_hour["hours"]])
                dataset.append(
                    {
                        "type": "spline",
                        "name": employee.full_name,
                        "data": data,
                    }
                )
        return dataset

    def _get_chart_data(self, request, *args, **kwargs):
        """

        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        employee_id = kwargs.get("employee_id__exact")
        if (
            not request.user.is_superuser
            and request.user.employee.id != employee_id
        ):
            raise PermissionDenied
        chart = {
            "label": "Weekly View",
            "total_hour": 0,
            "labels": [],
            "data": [],
        }

        filters = dict(
            [
                (key, request.GET.get(key))
                for key in dict(request.GET)
                if key not in ["p", "q", "o", "_changelist_filters"]
            ]
        )
        filters["employee_id__exact"] = employee_id
        employee_hours = (
            EmployeeProjectHour.objects.values("project_hour__date")
            .filter(**filters)
            .annotate(hours=Sum("hours"))
        )
        for employee_hour in employee_hours:
            chart.get("labels").append(
                employee_hour["project_hour__date"].strftime("%B %d %Y")
            )
            chart.get("data").append(employee_hour["hours"])
            chart["total_hour"] += employee_hour["hours"]
        return chart

    def employee_time_base_graph_view(self, request, *args, **kwargs):
        """
        Hour graph by employee id
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        current_date = datetime.now().today()
        start_date = current_date - relativedelta(months=6)
        if request.user.has_perm(
            "employee.view_employeeundertpm"
        ) is False and request.user.employee.id != kwargs.get(
            "employee_id__exact"
        ):
            raise PermissionDenied(
                "You do not have permission to access this feature."
            )

        initial_filter = {
            "project_hour__date__gte": request.GET.get(
                "project_hour__date__gte", start_date
            ),
            "project_hour__date__lte": request.GET.get(
                "project_hour__date__lte", current_date
            ),
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
            title=Employee.objects.get(pk=kwargs.get("employee_id__exact")),
        )
        return TemplateResponse(
            request,
            "admin/employee/employee_time_base_hour_graph.html",
            context,
        )

    def _get_employee_chart_data_by_daily_month_weekly_base(
        self, request, *args, **kwargs
    ):
        """
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        employee_id = kwargs.get("employee_id__exact")
        if (
            not request.user.is_superuser
            and request.user.has_perm("employee.view_employeeundertpm") is False
            and request.user.employee.id != kwargs.get("employee_id__exact")
        ):
            raise PermissionDenied
        employee_monthly_expected_hour = (
            Employee.objects.only("monthly_expected_hours")
            .get(id=employee_id)
            .monthly_expected_hours
        )

        chart = {
            "employee_id": employee_id,
            "daily": {
                "label": "Daily Hours",
                "total_hour": 0,
                "target_hour": round(
                    float(employee_monthly_expected_hour or 0) / 20, 2
                ),
                "labels": [],
                "data": [],
                "per_day_count": [],
            },
            "weekly": {
                "label": "Weekly Hours",
                "total_hour": 0,
                "target_hour": round(
                    float(employee_monthly_expected_hour or 0) / 4, 2
                ),
                "labels": [],
                "data": [],
                "per_day_count": [],
            },
            "monthly": {
                "label": "Monthly Hours",
                "total_hour": 0,
                "target_hour": round(
                    float(employee_monthly_expected_hour or 0), 2
                ),
                "labels": [],
                "data": [],
                "per_day_count": [],
            },
        }

        filters = kwargs.get("apply_filter")
        filters["employee_id__exact"] = employee_id
        if request.GET.get("project_hour__date__gte") is None:
            filters["project_hour__date__gte"] = filters[
                "project_hour__date__gte"
            ] - relativedelta(months=6)
        filtered_employee_hours = EmployeeProjectHour.objects.filter(
            **filters,
        )
        employee_monthly_hours = (
            filtered_employee_hours.annotate(
                month=TruncMonth("project_hour__date"),
            )
            .values("month")
            .annotate(monthly_hour=Sum("hours"))
            .order_by("month")
        )

        employee_hours = (
            EmployeeProjectHour.objects.select_related(
                "project_hour",
                "project_hour__project",
            )
            .filter(**filters)
            .only(
                "project_hour__date",
                "project_hour__project__title",
                "hours",
            )
            .order_by("project_hour__date")
        )

        projects_hour_by_date = dict()
        for employee_hour in employee_hours:
            date = employee_hour.project_hour.date.strftime("%b-%Y")
            item = projects_hour_by_date.get(date, [])
            if item:
                item.append(
                    [
                        employee_hour.project_hour.project.title,
                        employee_hour.hours,
                    ]
                )
            else:
                projects_hour_by_date[date] = [
                    [
                        employee_hour.project_hour.project.title,
                        employee_hour.hours,
                    ]
                ]
        for employee_monthly_hour in employee_monthly_hours:
            date = employee_monthly_hour.get("month")
            chart["monthly"]["labels"].append(date.strftime("%b-%Y"))
            chart["monthly"]["data"].append(
                employee_monthly_hour.get("monthly_hour")
            )
            chart["monthly"]["total_hour"] += employee_monthly_hour.get(
                "monthly_hour"
            )
            employee_hour_list = EmployeeProjectHour.objects.filter(
                employee_id=filters.get("employee_id__exact"),
                project_hour__date__month=date.month,
                project_hour__date__year=date.year,
            ).values(
                "id",
                "project_hour__date",
                "project_hour__project__title",
                "hours",
            )
            chart["monthly"]["per_day_count"].append(
                {
                    "project_by_project_hour": projects_hour_by_date.get(
                        date.strftime("%b-%Y"), []
                    ),
                    "all_project_hour": list(
                        [
                            {
                                "id": a.get("id"),
                                "date": a.get("project_hour__date").strftime(
                                    "%d-%b-%Y"
                                ),
                                "name": a.get("project_hour__project__title"),
                                "hour": a.get("hours"),
                            }
                            for a in employee_hour_list
                        ]
                    ),
                }
            )

        if request.GET.get("project_hour__date__gte") is None:
            filters["project_hour__date__gte"] = filters[
                "project_hour__date__gte"
            ] + relativedelta(months=6)

        weekly_employee_hours = (
            EmployeeProjectHour.objects.values("project_hour__date")
            .filter(**filters)
            .annotate(
                t_hours=Sum("hours"),
            )
            .order_by("project_hour__date")
        )

        employee_hours = (
            EmployeeProjectHour.objects.select_related(
                "project_hour",
                "project_hour__project",
            )
            .filter(**filters)
            .only(
                "project_hour__date",
                "project_hour__project__title",
                "hours",
            )
            .order_by("project_hour__date")
        )

        projects_hour_by_date = dict()
        for employee_hour in employee_hours:
            date = employee_hour.project_hour.date.strftime("%d-%b-%Y")
            item = projects_hour_by_date.get(date, [])
            if item:
                item.append(
                    [
                        employee_hour.project_hour.project.title,
                        employee_hour.hours,
                    ]
                )
            else:
                projects_hour_by_date[date] = [
                    [
                        employee_hour.project_hour.project.title,
                        employee_hour.hours,
                    ]
                ]

        employee_hour = EmployeeProjectHour.objects.filter(**filters)
        for weekly_employee_hour in weekly_employee_hours:
            date = weekly_employee_hour.get("project_hour__date").strftime(
                "%d-%b-%Y"
            )
            chart["weekly"]["labels"].append(date)
            chart["weekly"]["data"].append(weekly_employee_hour.get("t_hours"))

            employee_hour_list = employee_hour.filter(
                project_hour__date=weekly_employee_hour.get(
                    "project_hour__date"
                )
            ).values_list("hours", flat=True)
            chart["weekly"]["per_day_count"].append(
                {
                    "project_by_project_hour": projects_hour_by_date.get(
                        date, []
                    ),
                    "all_project_hour": list(employee_hour_list),
                }
            )
            chart["weekly"]["total_hour"] += weekly_employee_hour.get("t_hours")

        """
        for daily update
        """

        filters["created_at__date__lte"] = filters.pop(
            "project_hour__date__lte"
        )
        filters["created_at__date__gte"] = filters.pop(
            "project_hour__date__gte"
        )
        if request.GET.get("project_hour__date__gte") is None:
            filters["created_at__date__gte"] = filters[
                "created_at__date__gte"
            ] + relativedelta(months=5)
        # filters.pop("project_hour__date__gte")
        # filters.pop("project_hour__date__lte")
        # filters["created_at__date__gte"] = datetime.date.today() - relativedelta(days=30)
        # filters["created_at__date__lte"] = datetime.date.today()

        daily_employee_hours_filtered_queryset = (
            DailyProjectUpdate.objects.filter(
                # status="approved",
                **filters,
            )
        )
        daily_project_base_employee_hours = (
            daily_employee_hours_filtered_queryset.select_related(
                "project",
            )
            .only(
                "project__title",
                "hours",
            )
            .order_by("created_at__date")
        )
        daily_project_base_employee_hour_data = dict()
        for (
            daily_project_base_employee_hour
        ) in daily_project_base_employee_hours:
            date = daily_project_base_employee_hour.created_at.strftime(
                "%d-%b-%Y"
            )
            project_title = daily_project_base_employee_hour.project.title
            project_hour = daily_project_base_employee_hour.hours
            old_data = daily_project_base_employee_hour_data.get(date)
            if old_data:
                old_data.append([project_title, project_hour])
            else:
                daily_project_base_employee_hour_data[date] = [
                    [project_title, project_hour]
                ]

        daily_employee_hours = (
            daily_employee_hours_filtered_queryset.values(
                "created_at__date",
            )
            .annotate(total_hour=Sum("hours"))
            .order_by("created_at__date")
        )

        for daily_employee_hour in daily_employee_hours:
            date = daily_employee_hour.get("created_at__date").strftime(
                "%d-%b-%Y"
            )
            chart["daily"]["labels"].append(date)
            chart["daily"]["data"].append(daily_employee_hour.get("total_hour"))
            chart["daily"]["total_hour"] += daily_employee_hour.get(
                "total_hour"
            )
            chart["daily"]["per_day_count"].append(
                daily_project_base_employee_hour_data.get(date, [])
            )
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
            raise PermissionDenied(
                "You do not have permission to access this feature."
            )

        current_date = date().today()
        start_date = current_date - relativedelta(months=6)

        initial_filter = {
            "date__gte": request.GET.get("date__gte", start_date),
            "date__lte": request.GET.get("date__lte", current_date),
        }

        filter_form = DateFilterForm(initial={**initial_filter})
        context = dict(
            self.admin_site.each_context(request),
            chart=self._get_project_chart_data_by_month_weekly_base(
                request, *args, filters=initial_filter, **kwargs
            ),
            filter_form=filter_form,
            title=Project.objects.only("title")
            .get(pk=kwargs.get("project_id__exact"))
            .title,
        )
        return TemplateResponse(
            request, "admin/employee/time_base_project_hour_graph.html", context
        )

    def _get_project_chart_data_by_month_weekly_base(
        self, request, *args, **kwargs
    ):
        """
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        project_id = kwargs.get("project_id__exact")
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

        weekly_project_hours = (
            filtered_project_hours.values(
                "date",
            )
            .annotate(
                hours=Sum("hours"),
            )
            .order_by("date")
        )

        for weekly_project_hour in weekly_project_hours:
            chart["weekly"]["labels"].append(
                weekly_project_hour.get("date").strftime("%d-%b-%Y")
            )
            hour = weekly_project_hour.get("hours")
            chart["weekly"]["data"].append(hour)
            chart["weekly"]["total_hour"] += hour

        monthly_project_hours = (
            filtered_project_hours.values(
                "date__month",
                "date__year",
            )
            .annotate(
                total_hour=Sum("hours"),
            )
            .order_by("date__year", "date__month")
        )

        for monthly_project_hour in monthly_project_hours:
            month_num = str(monthly_project_hour.get("date__month")).zfill(2)
            month_abbr = calendar.month_abbr[int(month_num)]
            chart["monthly"]["labels"].append(
                f"{month_abbr}-{monthly_project_hour.get('date__year')}"
            )
            hour = monthly_project_hour.get("total_hour")
            chart["monthly"]["data"].append(hour)
            chart["monthly"]["total_hour"] += hour
        return chart

    def clinet_projects_graph(self, request, *args, **kwargs):
        if request.user.has_perm("employee.view_employeeundertpm") is False:
            raise PermissionDenied(
                "You do not have permission to access this feature."
            )
        current_date = date().today()
        start_date = current_date - relativedelta(months=6)
        initial_filter = {
            # "total_hour__gte" : request.GET.get("total_hour__gte"),
            # "total_hour__lte" : request.GET.get("total_hour__lte"),
            "date__gte": request.GET.get("date__gte", start_date),
            "date__lte": request.GET.get("date__lte", current_date),
        }
        filters = {key: value for key, value in initial_filter.items() if value}
        filter_form = ClientProjectsHourFilterForm(
            initial={**filters},
        )
        context = dict(
            self.admin_site.each_context(request),
            chart_data=self._get_client_all_projects_dataset(
                client_id=kwargs.get("client_id"), filters=filters
            ),
            filter_form=filter_form,
        )
        return TemplateResponse(
            request, "admin/employee/client_projects_hour_graph.html", context
        )

    def _get_client_all_projects_dataset(self, client_id: int, filters: dict):
        projects = (
            Project.objects.select_related("client")
            .only("title", "client")
            .filter(client_id=client_id)
        )
        dataset = dict()
        client = projects.first().client
        client_name = client.name
        client_id = client.id
        date_filters = {"date__gte": filters.pop("date__gte")}
        if filters.get("date__lte"):
            date_filters["date__lte"] = filters.pop("date__lte")
        # for all project
        # weekly projects hours
        all_project_hours = ProjectHour.objects.filter(
            project_id__in=projects.values_list("id", flat=True),
            **date_filters,
        )
        if projects.count() > 1 and all_project_hours.exists():
            weekly_all_project_hours = (
                all_project_hours.values("date")
                .annotate(total_hour=Sum("hours"))
                .filter(
                    **filters,
                )
                .order_by("date")
            )
            chart = {
                "weekly": {
                    "label": "Weekly Hours",
                    "client_name": client_name,
                    "client_id": client_id,
                    "labels": [],
                    "data": [],
                    "total_hour": 0,
                },
                "monthly": {
                    "label": "Monthly Hours",
                    "client_name": client_name,
                    "client_id": client_id,
                    "labels": [],
                    "data": [],
                    "total_hour": 0,
                },
            }
            for weekly_project_hour in weekly_all_project_hours:
                chart["weekly"]["labels"].append(
                    weekly_project_hour.get("date").strftime("%d-%b-%Y")
                )
                chart["weekly"]["data"].append(
                    weekly_project_hour.get("total_hour")
                )
                chart["weekly"]["total_hour"] += weekly_project_hour.get(
                    "total_hour"
                )
            monthly_all_project_hours = (
                all_project_hours.values("date__year", "date__month")
                .annotate(
                    total_hour=Sum("hours"),
                )
                .filter(
                    **filters,
                )
                .order_by("date__year", "date__month")
            )
            for monthly_project_hour in monthly_all_project_hours:
                month_num = str(monthly_project_hour.get("date__month")).zfill(
                    2
                )
                month_abbr = calendar.month_abbr[int(month_num)]
                chart["monthly"]["labels"].append(
                    f"{month_abbr}-{monthly_project_hour.get('date__year')}"
                )
                chart["monthly"]["data"].append(
                    monthly_project_hour.get("total_hour")
                )
                chart["monthly"]["total_hour"] += monthly_project_hour.get(
                    "total_hour"
                )
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
                weekly_project_hours = (
                    project_hours.values("date")
                    .annotate(total_hour=Sum("hours"))
                    .filter(
                        **filters,
                    )
                    .order_by("date")
                )
                chart = {
                    "weekly": {
                        "label": "Weekly Hours",
                        "client_name": client_name,
                        "client_id": client_id,
                        "labels": [],
                        "data": [],
                        "total_hour": 0,
                    },
                    "monthly": {
                        "label": "Monthly Hours",
                        "client_name": client_name,
                        "client_id": client_id,
                        "labels": [],
                        "data": [],
                        "total_hour": 0,
                    },
                }
                for project_hour in weekly_project_hours:
                    chart["weekly"]["labels"].append(
                        project_hour.get("date").strftime("%d-%b-%Y")
                    )
                    chart["weekly"]["data"].append(
                        project_hour.get("total_hour")
                    )
                    chart["weekly"]["total_hour"] += project_hour.get(
                        "total_hour"
                    )

                monthly_project_hours = (
                    project_hours.values(
                        "date__year",
                        "date__month",
                    )
                    .annotate(
                        total_hour=Sum("hours"),
                    )
                    .filter(
                        **filters,
                    )
                    .order_by(
                        "date__year",
                        "date__month",
                    )
                )
                for monthly_project_hour in monthly_project_hours:
                    month_num = str(
                        monthly_project_hour.get("date__month")
                    ).zfill(2)
                    month_abbr = calendar.month_abbr[int(month_num)]
                    chart["monthly"]["labels"].append(
                        f"{month_abbr}-{monthly_project_hour.get('date__year')}"
                    )
                    chart["monthly"]["data"].append(
                        monthly_project_hour.get("total_hour")
                    )
                    chart["monthly"]["total_hour"] += monthly_project_hour.get(
                        "total_hour"
                    )
                dataset[project.title] = {
                    "name": project.title,
                    "project_id": project.id,
                    **chart,
                }
        return dataset

    def all_employee_last_working_day_graph_view(
        self, request, *args, **kwargs
    ):
        if request.user.has_perm("employee.view_employeeundertpm") is False:
            raise PermissionDenied(
                "You do not have permission to access this feature."
            )

        if request.GET.get("created_at__date"):
            current_date = request.GET.get("created_at__date")
        else:
            current_date_time = datetime.datetime.now()
            current_date = current_date_time.date()
            weekday = current_date.weekday()
            if weekday in (5, 6):
                # get the last working date if current_date is Saturday or Sunday
                current_date = current_date - relativedelta(
                    days=1 if weekday == 5 else 2
                )
            elif current_date_time.time() < datetime.time(
                21, 0, 0
            ):  # define 9 PM, time(21, 0, 0)
                # get the last working date if current_time is less then 9 PM
                days = 3 if weekday == 0 else 1
                current_date = current_date - relativedelta(days=days)

        hours_filters = {
            key: request.GET.get(key)
            for key in ["total_hour__gte", "total_hour__lte"]
            if request.GET.get(key)
        }
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
        return TemplateResponse(
            request,
            "admin/employee/employees_last_working_day_hours.html",
            context,
        )

    def _all_employee_last_working_day_graph_data(
        self, date_filters, hours_filters
    ):
        daily_employee_hours = (
            DailyProjectUpdate.objects.filter(**date_filters)
            .select_related("employee", "project")
            .values("employee", "employee__full_name")
            .annotate(total_hour=Sum("hours"))
            .filter(**hours_filters)
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
            employee_projects[employee_id].append(
                [entry["project__title"], entry["hours"]]
            )

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
            chart["projects_hour"].append(
                employee_projects.get(employee_id, [])
            )
            chart["total_hour"] += daily_employee_hour["total_hour"]
        return chart

    def get_lead_choices(self):
        """Get all employees with lead=True"""
        return Employee.objects.filter(lead=True, active=True).order_by(
            "full_name"
        )

    def all_employee_monthly_graph_view(self, request, *args, **kwargs):
        if request.user.has_perm("employee.view_employeeundertpm") is False:
            raise PermissionDenied(
                "You do not have permission to access this feature."
            )

        # Get selected month (e.g., "2024-03")
        selected_month = request.GET.get("month")
        lead_filter = request.GET.get("lead")

        # Default to current month if not provided
        if not selected_month:
            today = timezone.now().date()
            selected_month = f"{today.year}-{today.month:02d}"
        filters = dict()
        # Parse year and month
        try:
            year, month = map(int, selected_month.split("-"))
        except (ValueError, AttributeError):
            today = timezone.now().date()
            year, month = today.year, today.month
            selected_month = f"{year}-{month:02d}"

        # Calculate month start and end dates
        start_date = date(year, month, 1)
        end_date = date(year, month, 1) + relativedelta(
            day=31
        )  # Last day of month

        # NEW: Skill filter
        skill_filter = request.GET.get("skill")
        skill_filters = {}
        if skill_filter:
            skill_filters["employee__employeeskill__skill_id"] = skill_filter
            filters[""] = ""

        # Prepare date filters
        date_filters = {
            "created_at__date__gte": start_date,
            "created_at__date__lte": end_date,
        }
        filters.update(date_filters)
        # Hour range filters
        hours_filters = {
            key: request.GET.get(key)
            for key in ["total_hour__gte", "total_hour__lte"]
            if request.GET.get(key)
        }

        # Initialize form
        initial_data = {"month": selected_month}
        if hours_filters:
            initial_data.update(hours_filters)

        if lead_filter:
            initial_data["lead"] = lead_filter

        date_filter_form = DailyUpdateDateFilterForm(initial=initial_data)

        if lead_filter:
            # Get projects for the selected lead

            date_filters = {
                "date__gte": start_date,
                "date__lte": end_date,
            }
            skill_filters[
                "employeeprojecthour__employee__employeeskill__skill_id"
            ] = skill_filter
            chart_data = self._lead_employee_monthly_graph_data(
                date_filters=date_filters,
                hours_filters=hours_filters,
                # project_ids=project_ids,
                skill_filters=skill_filters,
                lead_id=lead_filter,
            )
        else:
            # Use original function for regular employee filtering
            chart_data = self._employee_monthly_hour(
                start_date=start_date, end_date=end_date, request=request
            )

        skills = skills = Skill.objects.all().order_by("title")
        leads = self.get_lead_choices()
        context = dict(
            self.admin_site.each_context(request),
            chart=chart_data,
            date_filter_form=date_filter_form,
            month_choices=self.get_month_choices(),
            selected_month_value=selected_month,
            selected_month_name=datetime(year, month, 1).strftime("%B %Y"),
            skills=skills,
            selected_skill=skill_filter,
            selected_skill_name=Skill.objects.filter(id=skill_filter)
            .first()
            .title
            if skill_filter
            else None,
            leads=leads,
            selected_lead=lead_filter,
            selected_lead_name=Employee.objects.filter(id=lead_filter)
            .first()
            .full_name
            if lead_filter
            else None,
        )

        return TemplateResponse(
            request, "admin/employee/employees_monthly_hours.html", context
        )

    def _lead_employee_monthly_graph_data(
        self, date_filters, hours_filters, skill_filters, lead_id
    ):
        """
        Get manager/lead hours data using ProjectHour model,
        matching the structure of _employee_monthly_hour function.
        Filters by lead_id and aggregates by manager.
        """

        # Build complete filters
        filters = {**date_filters, "manager__id": lead_id, "status": "approved"}

        if skill_filters:
            filters.update(skill_filters)

        # Get total hours for the lead
        base_queryset = ProjectHour.objects.filter(**filters)

        # Aggregate by manager
        lead_hours = (
            base_queryset.select_related("manager")
            .values("manager", "manager__full_name")
            .annotate(total_hour=Sum("hours"))
            .order_by("total_hour")
        )

        # Apply hour range filters AFTER aggregation (matching _employee_monthly_hour pattern)
        min_hours = hours_filters.get("total_hour__gte")
        max_hours = hours_filters.get("total_hour__lte")

        if min_hours or max_hours:
            filtered_lead_hours = []
            for lead in lead_hours:
                total = lead["total_hour"]
                if min_hours is not None and total < float(min_hours):
                    continue
                if max_hours is not None and total > float(max_hours):
                    continue
                filtered_lead_hours.append(lead)
            lead_hours = filtered_lead_hours

        # Get project breakdown for the lead
        project_hours = (
            base_queryset.select_related("manager", "project")
            .values("project__title")
            .annotate(hours=Sum("hours"))
            .order_by("project__title")
        )

        # Build project lookup
        manager_id = lead_id
        manager_projects = {manager_id: []}
        for proj in project_hours:
            manager_projects[manager_id].append(
                [proj["project__title"], proj["hours"]]
            )

        # Build chart data (EXACT same structure)
        chart = {
            "label": "Lead's Project Hours",
            "labels": [],
            "data": [],
            "projects_hour": [],
            "employees_id": [],
            "total_hour": 0,
        }

        for lead in lead_hours:
            chart["labels"].append(lead["manager__full_name"])
            chart["data"].append(lead["total_hour"])
            chart["employees_id"].append(manager_id)
            chart["projects_hour"].append(manager_projects.get(manager_id, []))
            chart["total_hour"] += lead["total_hour"]

        return chart

    def lead_employee_monthly_graph_data(
        self, date_filters, hours_filters, skill_filters, lead_id
    ):
        """
        NEW FUNCTION: Filter by lead's projects instead of individual employee
        Shows all team members' hours on the lead's projects
        """
        # if not project_ids:
        #     # Return empty chart if no projects
        #     return {
        #         "label": "Lead's Project Hours",
        #         "labels": [],
        #         "data": [],
        #         "projects_hour": [],
        #         "employees_id": [],
        #         "total_hour": 0,
        #     }

        # Filter by the lead's projects
        base_queryset = ProjectHour.objects.filter(
            **date_filters, manager__id=lead_id, status="approved"
        )
        if skill_filters:
            base_queryset = base_queryset.filter(**skill_filters)

        # Get total hours per employee across all lead's projects
        employee_hours = (
            base_queryset.select_related("manager")
            .values("manager", "manager__full_name")
            .annotate(total_hour=Sum("hours"))
            .filter(**hours_filters)
            .order_by("total_hour")
        )

        # Get project breakdown per employee
        project_hours = (
            base_queryset.select_related("employee", "manager", "project")
            .values(
                "project", "project__title", "manager", "manager__full_name"
            )
            .annotate(hours=Sum("hours"))
            .order_by("employee", "project__title")
        )

        # Build project lookup
        employee_projects = {}
        for proj in project_hours:
            emp_id = proj["manager"]
            if emp_id not in employee_projects:
                employee_projects[emp_id] = []
            employee_projects[emp_id].append(
                [proj["project__title"], proj["hours"]]
            )

        # Build chart data (same structure as original)
        chart = {
            "label": "Lead's Project Hours",
            "labels": [],
            "data": [],
            "projects_hour": [],
            "employees_id": [],
            "total_hour": 0,
        }

        for emp in employee_hours:
            emp_id = emp["manager"]
            chart["labels"].append(emp["manager__full_name"])
            chart["data"].append(emp["total_hour"])
            chart["employees_id"].append(emp_id)
            chart["projects_hour"].append(employee_projects.get(emp_id, []))
            chart["total_hour"] += emp["total_hour"]

        return chart

    def get_month_choices(self):
        """Generate all months for current year (Jan-Dec)"""
        current_year = timezone.now().year
        choices = []

        for month in range(1, 13):
            value = f"{current_year}-{month:02d}"
            label = datetime(current_year, month, 1).strftime("%B %Y")
            choices.append((value, label))

        return choices

    def _all_employee_monthly_graph_data(
        self, date_filters, hours_filters, skill_filters
    ):
        """Get employee hours data for a given date range (single month)"""
        # Get total hours per employee
        queryset = EmployeeProjectHour.objects.filter(
            **date_filters, status="approved"
        )

        # NEW: Apply skill filter if provided
        if skill_filters:
            queryset = queryset.filter(**skill_filters)

        # Continue with aggregation
        employee_hours = (
            queryset.select_related("employee")
            .values("employee", "employee__full_name")
            .annotate(total_hour=Sum("hours"))
            .filter(**hours_filters)
            .order_by("total_hour")
        )

        # Get project breakdown per employee
        # project_queryset = DailyProjectUpdate.objects.filter(**date_filters)
        if skill_filters:
            queryset = queryset.filter(**skill_filters)

        project_hours = (
            queryset.select_related("employee", "project")
            .values("employee", "project__title")
            .annotate(hours=Sum("hours"))
            .order_by("employee", "project__title")
        )

        # Build project lookup
        employee_projects = {}
        for proj in project_hours:
            emp_id = proj["employee"]
            if emp_id not in employee_projects:
                employee_projects[emp_id] = []
            employee_projects[emp_id].append(
                [proj["project__title"], proj["hours"]]
            )

        # Build chart data
        chart = {
            "label": "Monthly Project Hours",
            "labels": [],
            "data": [],
            "projects_hour": [],
            "employees_id": [],
            "total_hour": 0,
        }

        for emp in employee_hours:
            emp_id = emp["employee"]
            chart["labels"].append(emp["employee__full_name"])
            chart["data"].append(emp["total_hour"])
            chart["employees_id"].append(emp_id)
            chart["projects_hour"].append(employee_projects.get(emp_id, []))
            chart["total_hour"] += emp["total_hour"]

        return chart

    def _employee_monthly_hour(self, start_date, end_date, request):
        """Get employee hours data using EmployeeProjectHour model,
        matching the structure of _all_employee_monthly_graph_data"""

        # Base filters
        filters = {
            "project_hour__date__gte": start_date,
            "project_hour__date__lte": end_date,
            # "project_hour__status": "approved"
        }

        # Skill filter
        skill = request.GET.get("skill")
        if skill:
            filters["employee__employeeskill__skill_id"] = skill

        # Lead filter (filtering by manager/lead field)
        lead = request.GET.get("lead")
        if lead:
            filters["project_hour__manager__id"] = lead

        hours_filters = {
            key: request.GET.get(key)
            for key in ["total_hour__gte", "total_hour__lte"]
            if request.GET.get(key)
        }

        if hours_filters:
            filters.update(hours_filters)

        # Get total hours per employee
        base_queryset = EmployeeProjectHour.objects.filter(**filters)

        employee_hours = (
            base_queryset.select_related("employee")
            .values("employee", "employee__full_name")
            .annotate(total_hour=Sum("hours"))
            .order_by("total_hour")
        )

        # Get project breakdown per employee
        project_hours = (
            base_queryset.select_related("employee", "project_hour__project")
            .values("employee", "project_hour__project__title")
            .annotate(hours=Sum("hours"))
            .order_by("employee", "project_hour__project__title")
        )

        # Build project lookup
        employee_projects = {}
        for proj in project_hours:
            emp_id = proj["employee"]
            if emp_id not in employee_projects:
                employee_projects[emp_id] = []
            employee_projects[emp_id].append(
                [proj["project_hour__project__title"], proj["hours"]]
            )

        # Build chart data (EXACT same structure)
        chart = {
            "label": "Monthly Project Hours",
            "labels": [],
            "data": [],
            "projects_hour": [],
            "employees_id": [],
            "total_hour": 0,
        }

        for emp in employee_hours:
            emp_id = emp["employee"]
            chart["labels"].append(emp["employee__full_name"])
            chart["data"].append(emp["total_hour"])
            chart["employees_id"].append(emp_id)
            chart["projects_hour"].append(employee_projects.get(emp_id, []))
            chart["total_hour"] += emp["total_hour"]

        return chart
