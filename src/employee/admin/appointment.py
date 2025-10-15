from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
# from employee.models.employee import Appointment
from django.utils.timesince import timesince

# @admin.register(Appointment)
# class AppointmentAdmin(admin.ModelAdmin):
#     list_display = ['employee', 'is_completed', 'waiting', 'subject', 'project', 'created_at']
#     actions = ('meeting_completed', )
#     list_filter = ['is_completed']
#     ordering = ['is_completed', 'created_at']

#     def has_add_permission(self, request) -> bool:
#         if request.user.is_superuser:
#             return True
#         return False;
#     def has_change_permission(self, request, obj=None) -> bool:
#         if request.user.is_superuser:
#            return True
#         return False
    
#     @admin.display(description="Employee")
#     def employee(self, obj):
#         return obj.created_by.employee.full_name
    
#     def waiting(self, obj):
#         if obj.is_completed:
#             return '-'
#         return timesince(obj.created_at)
    
#     @admin.action(description='Meeting completed')
#     def meeting_completed(self, request, queryset):
#         if request.user.is_superuser:
#             queryset.update(is_completed=True)
#             messages.success(request, 'The meeting status has been successfully updated.')

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         if not request.user.is_superuser:
#             return queryset.filter(created_by=request.user)
#         return queryset
        