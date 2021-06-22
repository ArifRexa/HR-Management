import datetime
from datetime import date

from django.contrib import admin
# Register your models here.
from django.db.models import Sum, Case, When, IntegerField, Count
from django.utils.html import format_html

from .admin_mixin.EmployeeAdmin import EmployeeAdmin
from .models import Employee, Overtime, SalaryHistory, Leave, LeaveAttachment, Resignation


class SalaryHistoryInline(admin.StackedInline):
    model = SalaryHistory
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(EmployeeAdmin, admin.ModelAdmin):
    actions = ['print_appointment_latter', 'increment_latter']
    inlines = (SalaryHistoryInline,)

    change_list_template = 'admin/employee/list.html'

    def get_list_display(self, request):
        list_display = ['employee_info', 'leave_info', 'salary_history', 'created_by', 'active']
        if not request.user.is_superuser:
            list_display.remove('salary_history')
        return list_display


@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'note', 'status')
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

    def change_view(self, request, *args, **kwargs):
        overtime = Overtime.objects.filter(id=kwargs['object_id']).first()
        self.readonly_fields = ()
        if not request.user.is_superuser:
            if overtime.status != 'pending':
                print('here')
                self.readonly_fields = super(OvertimeAdmin, self).get_fields(request)
        return super(OvertimeAdmin, self).change_view(request, *args, **kwargs)


class LeaveAttachmentInline(admin.TabularInline):
    model = LeaveAttachment
    extra = 0


@admin.register(Leave)
class LeaveManagement(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'total_leave', 'status', 'message')
    readonly_fields = ('note', 'total_leave')
    exclude = ['status_changed_at', 'status_changed_by']
    inlines = (LeaveAttachmentInline,)

    def get_fields(self, request, obj=None):
        fields = super(LeaveManagement, self).get_fields(request)
        if not request.user.is_superuser:
            admin_only = ['status', 'employee']
            for filed in admin_only:
                fields.remove(filed)
        return fields

    def change_view(self, request, *args, **kwargs):
        leave = Leave.objects.filter(id=kwargs['object_id']).first()
        print(self.readonly_fields)
        if not leave.status == 'pending' and not request.user.is_superuser:
            self.readonly_fields = super(LeaveManagement, self).get_fields(request)
        else:
            self.readonly_fields = ('note', 'total_leave')
        return super(LeaveManagement, self).change_view(request, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.employee_id:
            obj.employee_id = request.user.employee.id
        if request.user.is_superuser:
            obj.status_changed_by = request.user
            obj.status_changed_at = date.today()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ['status', 'leave_type', 'employee']
        if not request.user.is_superuser:
            list_filter.remove('employee')
        return list_filter


@admin.register(Resignation)
class ResignationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'message', 'date', 'status', 'approved_at', 'approved_by')

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
