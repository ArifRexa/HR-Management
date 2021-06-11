from datetime import datetime
from django.contrib import admin
from django.db.models import Sum

from account.models import SalarySheet, EmployeeSalary
from account.repository.SalarySheetRepository import SalarySheetRepository
from employee.models import Employee


class EmployeeSalaryInline(admin.TabularInline):
    model = EmployeeSalary
    extra = 0
    readonly_fields = ('employee', 'net_salary', 'overtime', 'project_bonus', 'leave_bonus', 'gross_salary',)
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(SalarySheet)
class SalarySheetAdmin(admin.ModelAdmin):
    list_display = ('date', 'created_at', 'total')
    fields = ('date',)
    inlines = (EmployeeSalaryInline,)

    def save_model(self, request, salary_sheet, form, change):
        salary = SalarySheetRepository()
        salary.save(request.POST['date'])

    def total(self, obj):
        return EmployeeSalary.objects.filter(salary_sheet_id=obj.id).aggregate(Sum('gross_salary'))['gross_salary__sum']
