from django.contrib import admin
from django.db.models.fields.related import ForeignKey
from employee.models.employee import Employee
from employee.models.employee_rating_models import EmployeeRating

@admin.register(EmployeeRating)
class EmployeeRatingAdmin(admin.ModelAdmin):
    list_display = ['rating_by', 'employee', 'score', 'comment', 'created_at']
    date_hierarchy = 'created_at'
    list_filter = ['employee']
    autocomplete_fields = ['employee']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs;
        return qs.filter(created_by_id=request.user.employee.id)
    
    @admin.display(description="Rating By")
    def rating_by(self, obj):
        return f'{obj.employee.full_name}'
    
    
    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj == None:
            field = form.base_fields['employee']
            field.widget.can_add_related = False
            field.widget.can_change_related = False
        return form