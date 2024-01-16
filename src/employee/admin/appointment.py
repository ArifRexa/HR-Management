from django.contrib import admin
from employee.models.employee import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'is_completed']
    list_filter = ['is_completed']
    
    @admin.display(description="Employee want to meet")
    def employee(self, obj):
        return obj.created_by.employee.full_name