import datetime
from datetime import timedelta

from django.contrib import admin
from django.db.models import Sum
from project_management.models import (
    EmployeeProjectHourGroupByEmployee,
)

from functools import update_wrapper
from django.urls import path
from employee.models.employee import Employee


@admin.register(EmployeeProjectHourGroupByEmployee)
class EmployeeProjectHourGroupByEmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "employee",
        "get_project",
        "hours",
    )
    list_filter = (
        "project_hour__project",
        "employee",
    )
    date_hierarchy = "created_at"
    change_list_template = "admin/weekly_update_groupby_employee.html"

    @admin.display(description="Project")
    def get_project(self, instance):
        return instance.project_hour.project.title

    class Media:
        css = {"all": ("css/list.css",)}
        js = ("js/list.js",)

    def custom_changelist_view(self, request, extra_context=None):
        today = datetime.datetime.now().date()
        yesterday = today - timedelta(days=1)

        filters = dict()
        for key, value in request.GET.items():
            if value != "":
                filters[key] = value
        if len(filters) == 0:
            filters["created_at__date"] = yesterday

        daily_project_update_data = dict()
        employee_hours = self.get_queryset(request).filter(**filters)

        for hours in employee_hours:
            key = hours.employee
            key.set_daily_hours(
                key.employeeprojecthour_set.filter(**filters)
                .aggregate(total_hours=Sum("hours"))
                .get("total_hours")
            )
            daily_project_update_data.setdefault(key, []).append(hours)

        sorted_data_set = dict(
            sorted(
                daily_project_update_data.items(),
                key=lambda x: x[0].daily_project_hours,
            )
        )

        my_context = {
            "daily_project_hours_data": sorted_data_set,
        }
        return super().changelist_view(request, extra_context=my_context)

    def get_urls(self):
        urls = super().get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        custome_urls = [
            path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),
            path(
                "", self.custom_changelist_view, name="groupby_employee_changelist_view"
            ),
        ]
        return custome_urls + urls

    def get_queryset(self, request):
        query_set = super().get_queryset(request)

        if not request.user.is_superuser and not request.user.has_perm(
            "project_management.see_all_employee_update"
        ):
            return query_set.filter(employee=request.user.employee.id)
        return query_set.filter(employee__active=True).exclude(employee_id__in=[30])

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []

        if obj:
            if request.user.employee.manager or request.user.employee.lead:
                if obj.manager != obj.employee and obj.manager == request.user.employee:
                    return ["employee", "manager", "project", "update"]
                else:
                    return []
            else:
                return self.readonly_fields

        else:
            if request.user.employee.manager or request.user.employee.lead:
                return []
            else:
                return self.readonly_fields
