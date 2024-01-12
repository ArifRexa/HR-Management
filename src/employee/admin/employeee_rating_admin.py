from django.contrib import admin
from django.db.models.fields.related import ForeignKey
from django.http.request import HttpRequest
from datetime import datetime, timedelta
from employee.models.employee_rating_models import EmployeeRating

@admin.register(EmployeeRating)
class EmployeeRatingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'rating_by', 'project', 'score', 'comment', 'created_at']
    date_hierarchy = 'created_at'
    list_filter = ['employee', 'project']
    autocomplete_fields = ['employee', 'project']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs;
        return qs.filter(created_by__id=request.user.id)
    
    def has_delete_permission(self, request, obj=None):
        delete_or_update_before = datetime.now() + timedelta(days=7)
        if obj is None:
            return False
        
        if obj.created_at > delete_or_update_before:
            return False
        return True

    @admin.display(description="Rating By")
    def rating_by(self, obj):
        return f'{obj.created_by.employee.full_name}'
    
    
    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj == None:
            field = form.base_fields['employee']
            field.widget.can_add_related = False
            field.widget.can_change_related = False
        return form