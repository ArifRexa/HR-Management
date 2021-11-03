from arabic_reshaper.reshaper_config import default_config
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig

from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery


class CustomAdminSite(admin.AdminSite):
    def each_context(self, request):
        employee_formal_summery = EmployeeNearbySummery()
        context = dict(
            super().each_context(request),
            leaves=employee_formal_summery.employee_leave_nearby,
            birthdays=employee_formal_summery.birthdays,
            increments=employee_formal_summery.increments,
            permanents=employee_formal_summery.permanents,
            anniversaries=employee_formal_summery.anniversaries
        )
        return context


class MyAdminConfig(AdminConfig):
    default_site = CustomAdminSite


admin_site = CustomAdminSite(name='myadmin')
