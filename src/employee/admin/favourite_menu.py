from django.contrib import admin
from employee.models import FavouriteMenu

@admin.register(FavouriteMenu)
class FavouriteMenuAdmin(admin.ModelAdmin):
    list_display = ('employee', 'menu_name')
    date_hierarchy = 'created_at'
    list_per_page = 20
    autocomplete_fields = ['employee']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(employee_id=request.user.employee)