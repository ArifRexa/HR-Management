from datetime import timedelta,datetime

from django.contrib import admin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from project_management.models import (
    EmployeeProjectHourGroupByEmployee,
)

from functools import update_wrapper
from django.urls import path
from employee.models.employee import Employee

@admin.register(EmployeeProjectHourGroupByEmployee)
class WeeklyEmployeeHoursAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "employee",
        "employee_monthly_expected_hours",
        "get_project",
        "hours",
        "get_manager",
    )

    list_filter = (
        "project_hour__project",
        "employee",
    )
    date_hierarchy = "project_hour__date"
    change_list_template = "admin/weekly_update_groupby_employee.html"

    @admin.display(description='Monthly Expected Hours')
    def employee_monthly_expected_hours(self, obj):
        monthly_hours = obj.employee.monthly_expected_hours or 0.0
        one_fourth_hours = monthly_hours / 4
        return f"{monthly_hours:.2f}({one_fourth_hours:.2f})"

    @admin.display(description="Project")
    def get_project(self, instance):
        return instance.project_hour.project.title

    @admin.display(description="Manager")
    def get_manager(self, instance):
        return instance.project_hour.manager.full_name

    class Media:
        css = {"all": ("css/list.css",)}
        js = ("js/list.js",)

    def changelist_view(self, request, extra_context=None):
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        filters = {}
        for key, value in request.GET.items():
            if value:
                filters[key] = value
        if not filters:
            filters["created_at__date"] = yesterday

        employee_hours_data = {}
        employee_hours = self.get_queryset(request).filter(**filters)

        for hours in employee_hours:
            key = hours.employee
            key.employee_hours = key.employeeprojecthour_set.filter(**filters).aggregate(total_hours=Coalesce(Sum("hours"), 0.0)).get("total_hours") or 0.0
            employee_hours_data.setdefault(key, []).append(hours)

        sorted_data_set = dict(sorted(employee_hours_data.items(), key=lambda x: x[0].employee_hours))
        
        extra_context = extra_context or {}
        extra_context['employee_hours_data'] = sorted_data_set

        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)
        
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),
            path(
                "", self.changelist_view, name="groupby_employee_changelist_view"
            ),
        ]

        return custom_urls + urls

    def get_queryset(self, request):
        query_set = super().get_queryset(request)

        if not request.user.is_superuser and not request.user.has_perm(
            "project_management.see_all_employee_update"
        ):
            return query_set.filter(employee=request.user.employee.id)
        return query_set.filter(employee__active=True).exclude(employee_id__in=[30])

    def has_module_permission(self, request):
        return True

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
