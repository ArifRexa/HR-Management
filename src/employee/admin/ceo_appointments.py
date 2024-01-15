from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from employee.models.employee import CEOAppointmentModel

@admin.register(CEOAppointmentModel)
class CEOAppointmentAdmin(admin.ModelAdmin):
    list_display = ['employee_name']

    def employee_name(self, obj):
        return obj.full_name
    
    def get_queryset(self, request):
        return super().get_queryset(request)