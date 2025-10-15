from django.contrib import admin
from ..models import VivaConfig
from ..models.viva_config import ExcludedDates

class ExcludedDatesInline(admin.TabularInline):
    model = ExcludedDates
    extra = 1


class VivaConfigAdmin(admin.ModelAdmin):
    list_display = ['job_post', 'duration', 'start_date', 'end_date', 'start_time', 'end_time']
    list_filter = ['job_post', 'start_date', 'end_date']
    search_fields = ['job_post']
    inlines = [ExcludedDatesInline]
    
    def has_module_permission(self, request):
        return False


admin.site.register(VivaConfig, VivaConfigAdmin)
