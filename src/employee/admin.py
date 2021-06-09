from django.contrib import admin

# Register your models here.
from .models import Employee, Overtime


def make_published(modeladmin, request, queryset):
    queryset.update(status='p')


make_published.short_description = "Print Appointment Latter"


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'designation', 'leave', 'created_at', 'created_by')
    actions = [make_published]


@admin.register(Overtime)
class Overtime(admin.ModelAdmin):
    list_display = ('employee', 'date', 'note')
    date_hierarchy = 'date'
