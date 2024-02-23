from django.contrib import admin
from ..models import VivaConfig


class VivaConfigAdmin(admin.ModelAdmin):
    list_display = ['job_post', 'duration', 'start_date', 'end_date', 'start_time', 'end_time']
    list_filter = ['job_post', 'start_date', 'end_date']
    search_fields = ['job_post']


admin.site.register(VivaConfig, VivaConfigAdmin)
