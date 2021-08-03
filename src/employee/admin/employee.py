from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.utils.text import slugify
from config.utils.pdf import PDF
from employee.admin_mixin.EmployeeActions import EmployeeActions
from employee.admin_mixin.EmployeeAdminListView import EmployeeAdminListView
from employee.admin_mixin.EmployeeExtraUrls import EmployeeExtraUrls
from employee.models import SalaryHistory, Employee, BankAccount
from employee.models.attachment import Attachment


class SalaryHistoryInline(admin.TabularInline):
    model = SalaryHistory

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 60})}
    }

    def get_extra(self, request, obj=None, **kwargs):
        return 1 if not obj else 0


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0


class BankAccountInline(admin.TabularInline):
    model = BankAccount

    def get_extra(self, request, obj=None, **kwargs):
        return 1 if not obj else 0


@admin.register(Employee)
class EmployeeAdmin(EmployeeAdminListView, EmployeeActions, EmployeeExtraUrls, admin.ModelAdmin):
    inlines = (AttachmentInline, SalaryHistoryInline, BankAccountInline)
    search_fields = ['full_name', 'email', 'salaryhistory__payable_salary']
    list_per_page = 20

    def get_list_display(self, request):
        list_display = ['full_name', 'employee_info', 'leave_info', 'salary_history', 'permanent_status', 'active']
        if not request.user.is_superuser:
            list_display.remove('salary_history')
        return list_display

    def get_queryset(self, request):
        if not request.user.is_superuser:
            return super(EmployeeAdmin, self).get_queryset(request).filter(user__id=request.user.id)
        return super(EmployeeAdmin, self).get_queryset(request)

    def get_actions(self, request):
        if not request.user.is_superuser:
            return []
        return super(EmployeeAdmin, self).get_actions(request)

    # def get_list_filter(self, request):
    #     if request.user.is_superuser:
    #         return ['active', 'permanent_date']
    #     return []
