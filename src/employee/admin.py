from django.contrib import admin

# Register your models here.
from .models import Employee, Overtime, SalaryHistory


def make_published(modeladmin, request, queryset):
    queryset.update(status='p')


make_published.short_description = "Print Appointment Latter"


class SalaryHistoryInline(admin.StackedInline):
    model = SalaryHistory
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'designation', 'leave', 'created_at', 'created_by')
    actions = [make_published]
    inlines = (SalaryHistoryInline,)


@admin.register(Overtime)
class Overtime(admin.ModelAdmin):
    list_display = ('employee', 'date', 'note')
    date_hierarchy = 'date'
