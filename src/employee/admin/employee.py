from django.contrib import admin
from django.utils.text import slugify
from config.utils.pdf import PDF
from employee.admin_mixin.EmployeeActions import EmployeeActions
from employee.admin_mixin.EmployeeAdminListView import EmployeeAdminListView
from employee.models import SalaryHistory, Employee
from employee.models.attachment import Attachment


class SalaryHistoryInline(admin.StackedInline):
    model = SalaryHistory

    def get_extra(self, request, obj=None, **kwargs):
        return 1 if not obj else 0


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(EmployeeAdminListView, EmployeeActions, admin.ModelAdmin):
    inlines = (AttachmentInline, SalaryHistoryInline)
    search_fields = ['full_name', 'email', 'salaryhistory__payable_salary']

    def get_list_display(self, request):
        list_display = ['id', 'employee_info', 'leave_info', 'salary_history', 'permanent_status', 'active']
        if not request.user.is_superuser:
            list_display.remove('salary_history')
        return list_display

    # def get_list_filter(self, request):
    #     if request.user.is_superuser:
    #         return ['active', 'permanent_date']
    #     return []
