from datetime import date

from django.contrib import admin
# Register your models here.
from django.db.models import Sum, Case, When, IntegerField, Count
from django.utils.html import format_html

from .models import Employee, Overtime, SalaryHistory, Leave, LeaveAttachment


class SalaryHistoryInline(admin.StackedInline):
    model = SalaryHistory
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_info', 'leave_info', 'salary_history', 'created_by')
    actions = ['print_appointment_latter', 'increment_latter']
    inlines = (SalaryHistoryInline,)

    change_list_template = 'admin/employee/list.html'

    def employee_info(self, obj):
        return format_html(
            f"<dl>"
            f"<dt>Name</dt>  <dd>: {obj.full_name}</dd>"
            f"<dt>Designation</dt> <dd>: {obj.designation} {'*' if obj.manager else ''}</dd>"
            f"<dt>Joining Date</dt> <dd>: {obj.joining_date}</dd>"
            f"</dl>"
        )

    def leave_info(self, obj):
        approved_leave = obj.leave_set.filter(status='approved')
        return format_html(
            f"<dl>"
            f"<dt>Casual</dt>  <dd>{self.sum_total_leave(approved_leave.filter(leave_type='casual'))}/{obj.leave_management.casual_leave}</dd>"
            f"<dt>Medical</dt>  <dd>{self.sum_total_leave(approved_leave.filter(leave_type='medical'))}/{obj.leave_management.medical_leave}</dd>"
            f"<dt>Non Paid</dt>  <dd>{self.sum_total_leave(approved_leave.filter(leave_type='non_paid'))}</dd>"
            f"</dl>"
        )

    def salary_history(self, obj):
        history = obj.salaryhistory_set.order_by('-id')[:2]
        return format_html(
            f"<dl>"
            f"<dt>Current Salary</dt>  <dd>{history[0].payable_salary} - {history[0].active_from}</dd>"
            f"<dt>Last Salary</dt>  <dd>{history[1].payable_salary if len(history) > 1 else '--'}</dd>"
            f"</dl>"
        )

    def sum_total_leave(self, obj):
        return obj.aggregate(total=Sum('total_leave'))['total']

    def print_appointment_latter(self):
        pass

    def increment_latter(self):
        pass


@admin.register(Overtime)
class Overtime(admin.ModelAdmin):
    list_display = ('employee', 'date', 'note')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ['employee', 'date']
        if not request.user.is_superuser:
            list_filter.remove('employee')
        return list_filter


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
