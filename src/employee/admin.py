from datetime import datetime, timedelta, date

from django.contrib import admin

# Register your models here.
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import format_html

from .models import Employee, Overtime, SalaryHistory, Leave, LeaveAttachment


def make_published(modeladmin, request, queryset):
    queryset.update(status='p')


make_published.short_description = "Print Appointment Latter"


class SalaryHistoryInline(admin.StackedInline):
    model = SalaryHistory
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_info', 'full_name', 'designation', 'created_at', 'created_by')
    actions = [make_published]
    inlines = (SalaryHistoryInline,)

    def employee_info(self, obj):
        return format_html(
            f"Name : {obj.full_name} <br>"
            f"Designation : {obj.designation}"
        )


@admin.register(Overtime)
class Overtime(admin.ModelAdmin):
    list_display = ('employee', 'date', 'note')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ['employee', 'date']
        if not request.user.is_superuser:
            list_filter.remove('employee')
        return list_filter


class LeaveAttachmentInline(admin.TabularInline):
    model = LeaveAttachment
    extra = 0


@admin.register(Leave)
class LeaveManagement(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'total_leave', 'status', 'message')
    readonly_fields = ('note', 'total_leave')
    exclude = ['status_changed_at', 'status_changed_by']
    inlines = (LeaveAttachmentInline,)

    def get_fields(self, request, obj=None):
        fields = super(LeaveManagement, self).get_fields(request)
        if not request.user.is_superuser:
            admin_only = ['status', 'employee']
            for filed in admin_only:
                fields.remove(filed)
        return fields

    def save_model(self, request, obj, form, change):
        if not obj.employee_id:
            obj.employee_id = request.user.employee.id
        if request.user.is_superuser:
            obj.status_changed_by = request.user
            obj.status_changed_at = date.today()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ['status', 'leave_type', 'employee']
        if not request.user.is_superuser:
            list_filter.remove('employee')
        return list_filter
