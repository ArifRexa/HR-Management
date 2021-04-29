from django.contrib import admin

# Register your models here.
from .models import Employee


def make_published(modeladmin, request, queryset):
    queryset.update(status='p')


make_published.short_description = "Print Appointment Latter"


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'designation', 'pay_scale', 'leave', 'created_at', 'created_by')
    actions = [make_published]


admin.site.register(Employee, EmployeeAdmin)
