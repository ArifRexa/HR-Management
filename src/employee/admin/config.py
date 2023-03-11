from django.contrib import admin
from employee.models.config import Config


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    
    def has_module_permission(self, request):
        return False