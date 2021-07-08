from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

now = timezone.now()


class RecentEdit(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        three_day_earlier = timezone.now() - timedelta(days=2)

        if obj is not None:
            if obj.created_at <= three_day_earlier and not request.user.is_superuser:
                return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
        return ()


class PendingStatusEdit(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            if obj.status == 'pending' and not request.user.is_superuser:
                return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
        return []
