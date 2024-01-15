from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.contrib import admin
from django import forms
from datetime import datetime, timedelta
from employee.models.employee_rating_models import EmployeeRating

class EmployeeRatingForm(forms.ModelForm):
    model = EmployeeRating
    fields = '__all__'

    def clean(self):
        clean_data = super().clean()

        if 'employee' in clean_data:
            is_provided = EmployeeRating.objects.filter(created_at__month=datetime.now().month, employee=clean_data.employee).exists()
            if is_provided and clean_data.id == None:
                raise ValidationError({'employee': 'You already given the rating'})
        
            delete_or_update_before = datetime.now() + timedelta(days=7)
            if clean_data.id != None and clean_data.created_at > delete_or_update_before:
                raise ValidationError({"comment": "You can\'t update your rating!"})

            if datetime.now().weekday() != 4:
                raise ValidationError({"comment": "You can\'t make rating today. You can try at friday."})
        return clean_data
         
@admin.register(EmployeeRating)
class EmployeeRatingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'rating_by', 'project', 'score', 'comment', 'created_at']
    date_hierarchy = 'created_at'
    list_filter = ['employee', 'project']
    autocomplete_fields = ['employee', 'project']
    form = EmployeeRatingForm

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
    
