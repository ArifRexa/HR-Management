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
    autocomplete_fields = ['user', 'designation']
    change_list_template = 'admin/employee/list/index.html'

    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        data = request.GET.dict()

        app_label = data.get('app_label')
        model_name = data.get('model_name')

        # TODO: Fix Permission
        if  request.user.is_authenticated and app_label == 'project_management' and model_name == 'codereview':
            qs = Employee.objects.filter(active=True, full_name__icontains=search_term)
        return qs, use_distinct

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
class EmployeeDetails(admin.ModelAdmin):
    list_display = ('employee', 'get_designation', 'get_phone', 'get_blood_group')
    list_filter = ('active',)
    search_fields = ('employee__full_name', 'employee__phone')

    @admin.display(description='Designation', ordering='employee__designation')
    def get_designation(self, obj: EmployeeLunch):
        return obj.employee.designation

    @admin.display(description='Phone')
    def get_phone(self, obj: EmployeeLunch):
        return obj.employee.phone

    @admin.display(description='Blood Group', ordering='employee__blood_group')
    def get_blood_group(self, obj: EmployeeLunch):
        return obj.employee.blood_group

    def get_queryset(self, request):
        queryset = super(EmployeeDetails, self).get_queryset(request)
        return queryset.filter(employee__active=True)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        elif request.user.employee == obj.employee:
            return ['employee']
        return ['employee', 'active']