from django.contrib import admin
from django.db.models.fields.related import ForeignKey
from employee.models.sqa import SQARating
from employee.models.employee import Employee

@admin.register(SQARating)
class SQARatingAdmin(admin.ModelAdmin):
    list_display = ['rating_by', 'sqa', 'score', 'created_at']
    date_hierarchy = 'created_at'
    list_filter = ['sqa']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs;
        return qs.filter(created_by_id=request.user.employee.id)
    
    @admin.display(description="Rating By")
    def rating_by(self, obj):
        return f'{obj.created_by.first_name} {obj.created_by.last_name}'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "sqa":
            kwargs['queryset'] = Employee.objects.filter(designation__title='SQA')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj == None:
            field = form.base_fields['sqa']
            field.widget.can_add_related = False
            field.widget.can_change_related = False
        return form