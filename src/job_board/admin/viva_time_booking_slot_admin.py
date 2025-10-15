from django.contrib import admin
from ..models import JobVivaTimeSlot


# @admin.register(JobVivaTimeSlot)
# class JobVivaTimeSlotAdmin(admin.ModelAdmin):
#     list_display = ('job_post', 'candidate', 'duration', 'start_time', 'end_time', 'date')

# class JobVivaTimeSlotAdmin(admin.ModelAdmin):
#     list_display = ['job_post', 'candidate', 'start_time', 'end_time', 'interview_duration', 'date']
#
#     def interview_duration(self, obj):
#         # Calculate the interview duration based on start and end times
#         start_time = obj.start_time
#         end_time = obj.end_time
#         duration = end_time - start_time
#         return duration
#
#     interview_duration.short_description = 'Interview Duration'
from datetime import datetime

class JobVivaTimeSlotAdmin(admin.ModelAdmin):
    list_display = ['job_post', 'candidate', 'date', 'start_time', 'end_time', 'interview_duration']
    date_hierarchy = "date"
    
    def has_module_permission(self, request):
        return False
    
    def interview_duration(self, obj):
        # Convert start_time and end_time to datetime objects
        start_datetime = datetime.combine(datetime.today(), obj.start_time)
        end_datetime = datetime.combine(datetime.today(), obj.end_time)

        # Calculate the interview duration
        duration = end_datetime - start_datetime
        return duration

    interview_duration.short_description = 'Interview Duration'
admin.site.register(JobVivaTimeSlot, JobVivaTimeSlotAdmin)
