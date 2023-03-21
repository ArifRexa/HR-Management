from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

now = timezone.now()


class RecentEdit(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        seven_day_earlier = timezone.now() - timedelta(days=6)
        if obj is not None:
            if obj.created_at <= seven_day_earlier and not request.user.is_superuser and not request.user.has_perm('project_management.weekly_project_hours_approve'):
                return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
        return ()


class PendingStatusEdit(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            if obj.status == 'pending' and not request.user.is_superuser:
                return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
        return []
