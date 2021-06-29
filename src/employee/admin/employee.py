from django.contrib import admin
from employee.admin_mixin.EmployeeAdmin import EmployeeAdmin
from employee.models import SalaryHistory, Employee


class SalaryHistoryInline(admin.StackedInline):
    model = SalaryHistory

    def get_extra(self, request, obj=None, **kwargs):
        if not obj:
            return 1
        return 0


@admin.register(Employee)
class EmployeeAdmin(EmployeeAdmin, admin.ModelAdmin):
    actions = ['print_appointment_latter', 'increment_latter']
    inlines = (SalaryHistoryInline,)

    change_list_template = 'admin/employee/list.html'

    def get_list_display(self, request):
        list_display = ['id', 'employee_info', 'leave_info', 'salary_history', 'permanent_status', 'active']
        if not request.user.is_superuser:
            list_display.remove('salary_history')
        return list_display
