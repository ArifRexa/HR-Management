from django.contrib import admin
from django.db import models
from django.forms import Textarea

from employee.admin.employee._actions import EmployeeActions
from employee.admin.employee.extra_url.index import EmployeeExtraUrls
from employee.admin.employee._inlines import EmployeeInline
from employee.admin.employee._list_view import EmployeeAdminListView
from employee.models import SalaryHistory, Employee, BankAccount, EmployeeSkill
from employee.models.attachment import Attachment
from employee.models.employee import EmployeeLunch


@admin.register(Employee)
class EmployeeAdmin(EmployeeAdminListView, EmployeeActions, EmployeeExtraUrls, EmployeeInline, admin.ModelAdmin):
    search_fields = ['full_name', 'email', 'salaryhistory__payable_salary', 'employeeskill__skill__title']
    list_per_page = 20
    ordering = ['-active']
    list_filter = ['active', 'permanent_date']

    change_list_template = 'admin/employee/list/index.html'

    def get_list_display(self, request):
        list_display = ['employee_info', 'leave_info', 'salary_history', 'skill', 'permanent_status']
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


@admin.register(EmployeeLunch)
class EmployeeLunchAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_phone', 'get_lunch_status')
    list_filter = ('active',)
    search_fields = ('employee__full_name', 'employee__phone')

    @admin.display(boolean=True, description='Lunch Status')
    def get_lunch_status(self, obj):
        return obj.active

    @admin.display(description='Phone')
    def get_phone(self, obj: EmployeeLunch):
        return obj.employee.phone

    # def get_queryset(self, request):
    #     queryset = super(EmployeeLunchAdmin, self).get_queryset(request)
    #     if request.user.is_superuser or request.user.has_perm('employee.can_see_all_lunch'):
    #         return queryset.filter(employee__active=True)
    #     else:
    #         return queryset.filter(employee_id=request.user.employee.id)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        elif request.user.employee == obj.employee:
            return ['employee']
        return ['employee', 'active']
