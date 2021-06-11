from django.contrib import admin

# Register your models here.
from django.db import models

from .models import Employee, Overtime, SalaryHistory, Leave, LeaveAttachment


def make_published(modeladmin, request, queryset):
    queryset.update(status='p')


make_published.short_description = "Print Appointment Latter"


class SalaryHistoryInline(admin.StackedInline):
    model = SalaryHistory
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'designation', 'created_at', 'created_by')
    actions = [make_published]
    inlines = (SalaryHistoryInline,)


@admin.register(Overtime)
class Overtime(admin.ModelAdmin):
    list_display = ('employee', 'date', 'note')
    date_hierarchy = 'date'


class LeaveAttachmentInline(admin.TabularInline):
    model = LeaveAttachment
    extra = 0


@admin.register(Leave)
class LeaveManagement(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'total_leave', 'status', 'status_changed_by', 'status_changed_at')
    readonly_fields = ('note',)
    inlines = (LeaveAttachmentInline,)
