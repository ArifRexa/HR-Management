from django.contrib import admin

from employee.models import Overtime
from django.contrib import messages


@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'short_note', 'status')
    date_hierarchy = 'date'
    list_filter = ("employee",)
    actions = ('approve_selected',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.has_perm('employee.can_approve_overtime'):
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ['employee', 'date', 'status']
        if not request.user.is_superuser or request.user.has_perm('employee.can_approve_overtime'):
            list_filter.remove('employee')
        return list_filter

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request)

        if not (request.user.is_superuser or request.user.has_perm('employee.can_approve_overtime')):
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
                print([item.name for item in obj._meta.fields])
                if overtime.status != 'pending':
                    return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
        return ()

    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if 'approve_selected' in actions:
    #         del actions['approve_selected']
    #     if request.user.is_superuser or request.user.has_perm('employee.can_approve_overtime'):
    #         actions['approve_selected'] = (self.approve_selected, 'approve_selected', 'Approve Selected Overtimes')
    #     return actions

    @admin.action(description='Approve Selected Overtimes')
    def approve_selected(self, request, queryset):
        if request.user.is_superuser or request.user.has_perm('employee.can_approve_overtime'):
            queryset.update(status='approved')
        else:
            messages.error(request, "You don't have enough permission")

    def has_module_permission(self, request):
        return False
