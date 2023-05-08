from math import floor

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Sum
from django.http import HttpResponse
from django.utils.html import format_html
from num2words import num2words
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from account.admin.salary.actions import SalarySheetAction
from account.models import SalarySheet, EmployeeSalary
from account.repository.SalarySheetRepository import SalarySheetRepository


class EmployeeSalaryInline(admin.TabularInline):
    model = EmployeeSalary
    extra = 0
    exclude = [
        'provident_fund',
        'code_quality_bonus',
    ]
    readonly_fields = ('employee', 'net_salary', 'overtime',
                       'project_bonus', 'leave_bonus', 'festival_bonus', 
                       'food_allowance', 'loan_emi', 
                       # 'provident_fund', 'code_quality_bonus', 
                       'gross_salary', #'get_details'
    ) 
    can_delete = False

    @admin.display(description="More Info")
    def get_details(self, obj, *args, **kwargs):
        return format_html(f'<a href="/media/temp_emp_salary/{obj.employee.id}.txt" download>Download</a>')


    def has_add_permission(self, request, obj):
        return False


@admin.register(SalarySheet)
class SalarySheetAdmin(SalarySheetAction, admin.ModelAdmin):
    list_display = ('date', 'created_at', 'total', 'total_employee', 'festival_bonus')
    fields = ('date', 'festival_bonus')
    inlines = (EmployeeSalaryInline,)

    def save_model(self, request, salary_sheet, form, change):
        # TODO : add festival bonus
        salary = SalarySheetRepository(request.POST['date'])
        if 'festival_bonus' in request.POST and request.POST['festival_bonus'] == 'on':
            salary.festival_bonus = True
        salary.save()

    def total(self, obj):
        total_value = EmployeeSalary.objects.filter(salary_sheet_id=obj.id).aggregate(Sum('gross_salary'))[
            'gross_salary__sum']
        return format_html(
            f'<b>{intcomma(floor(total_value))}</b> <br>'
            f'{num2words(floor(total_value)).capitalize()}'
        )

    def total_employee(self, obj):
        return obj.employeesalary_set.count()
