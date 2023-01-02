from django.contrib import admin

from employee.models import Overtime


@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'short_note', 'status')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ['employee', 'date', 'status']
        if not request.user.is_superuser:
            list_filter.remove('employee')
        return list_filter

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request)
        if not request.user.is_superuser:
            fields.remove('employee')
            fields.remove('status')
        return fields

    def save_model(self, request, obj, form, change):
        if not obj.employee_id:
            obj.employee_id = request.user.employee.id
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            overtime = Overtime.objects.filter(id=request.resolver_match.kwargs['object_id']).first()
            if not request.user.is_superuser:
                if overtime.status != 'pending':
                    return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
        return ()
    
    def has_module_permission(self, request):
        return False
