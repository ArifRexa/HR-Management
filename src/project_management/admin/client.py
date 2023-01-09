from django.contrib import admin

from project_management.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')

    def has_module_permission(self, request):
        return False
