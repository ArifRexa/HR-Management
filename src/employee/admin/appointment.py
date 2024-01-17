from django.contrib import admin, messages
from employee.models.employee import Appointment
from django.utils.timesince import timesince

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'is_completed', 'waiting', 'subject', 'project', 'created_at']
    actions = ('meeting_completed', )
    list_filter = ['is_completed']
    ordering = ['is_completed', 'created_at']
    
    @admin.display(description="Employee")
    def employee(self, obj):
        return obj.created_by.employee.full_name
    
    def waiting(self, obj):
        if obj.is_completed:
            return '-'
        return timesince(obj.created_at)
    
    @admin.action(description='Meeting completed')
    def meeting_completed(self, request, queryset):
        if request.user.is_superuser:
            queryset.update(is_completed=True)
            messages.success(request, 'The meeting status has been successfully updated.')
        