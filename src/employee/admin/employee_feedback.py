from django.contrib import admin

from django.urls import path

from employee.models import EmployeeFeedback
from employee.views import employee_feedback

@admin.register(EmployeeFeedback)
class EmployeeFeedbackAdmin(admin.ModelAdmin):
    list_display = ('employee', 'feedback', 'rating')
    #list_editable = ('employee',)
    list_filter = ('employee', 'rating')
    search_fields = ('employee__full_name',)
    autocomplete_fields = ('employee',)

    def get_urls(self):
        urls = super(EmployeeFeedbackAdmin, self).get_urls()

        employee_online_urls = [
            path('employee-feedback/', employee_feedback, name='employee_feedback'),
        ]

        return employee_online_urls + urls
