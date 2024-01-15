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
        request = self.request

        if clean_data.get('employee'):
            before_week = datetime.now() - timedelta(days=7)
            is_provided = EmployeeRating.objects.filter(
                                                        created_at__gt = before_week, 
                                                        employee = clean_data.get('employee'), 
                                                        project = clean_data.get('project'),
                                                        created_by = request.user).exists()
            if is_provided and self.instance.id is None:
                raise forms.ValidationError({'employee': 'You already given the rating. Plesae try again 7 days later.'})

            if self.instance.id and self.instance.created_at <= before_week:
                raise ValidationError({"comment": "You can\'t update your rating!"})
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
        form.request = request
        return form
    
