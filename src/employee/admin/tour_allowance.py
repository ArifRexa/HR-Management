from django.contrib import admin
from employee.models import TourAllowance
from django.urls import path 


# admin.site.register(TourAllowance)

@admin.register(TourAllowance)
class TourAllowanceAdmin(admin.ModelAdmin):
    filter_horizontal = ('employees',)

    def has_module_permission(self, request): 
        return False
