from datetime import date

from django.contrib import admin

from config.admin import RecentEdit
from employee.models import Resignation


@admin.register(Resignation)
class ResignationAdmin(RecentEdit, admin.ModelAdmin):
    list_display = ('employee', 'short_message', 'date', 'status', 'approved_at', 'approved_by')
    search_fields = ['employee__full_name', 'message']

    def get_fields(self, request, obj=None):
        fields = super(ResignationAdmin, self).get_fields(request)
        if not request.user.is_superuser:
            fields.remove('employee')
            fields.remove('status')
        return fields

    def get_queryset(self, request):
        qs = super(ResignationAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee_id=request.user.employee)

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser and request.POST.get('status') != 'pending':
            obj.approved_at = date.today()
            obj.approved_by = request.user
        else:
            obj.employee = request.user.employee
        super().save_model(request, obj, form, change)
    
    def has_module_permission(self, request):
        return False
