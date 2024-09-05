from math import floor
from typing import Any, Optional, Sequence

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Sum
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.utils.html import format_html
from num2words import num2words
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from account.admin.salary.actions import SalarySheetAction
from account.models import SalarySheet, EmployeeSalary
from account.repository.SalarySheetRepository import SalarySheetRepository
from employee.models.employee import LateAttendanceFine


class EmployeeSalaryInline(admin.TabularInline):
    model = EmployeeSalary
    extra = 0
    template= "admin/employee_salary.html"
    exclude = [
        'provident_fund',
        'code_quality_bonus',
        'festival_bonus',
        'device_allowance',
        "loan_emi"
    ]
    readonly_fields = (
        'employee', 'net_salary', 'overtime',
        'project_bonus', 'leave_bonus', #'festival_bonus', 
        'food_allowance', 'get_tax_loan',"get_salary_loan",

        # 'provident_fund', 'code_quality_bonus',
        'festival_bonus',
        'get_late_fine',
        'gross_salary', #'get_details',

    )
    superadminonly_fields = (
        'net_salary',
        'leave_bonus',
        'gross_salary',
    )

    can_delete = False

    def get_tax_loan(self, obj):
        return obj.loan_emi
    get_tax_loan.short_description = 'Tax Loan'

    def get_exclude(self, request, obj=None):
        exclude = list(super().get_exclude(request, obj))
        if not request.user.is_superuser and not request.user.has_perm('account.can_see_salary_on_salary_sheet'):
            exclude.extend(self.superadminonly_fields)
        return exclude
    def get_late_fine(self, obj):
        
        fine = LateAttendanceFine.objects.filter(
                    employee=obj.employee,
                    month=obj.salary_sheet.date.month,
                    year=obj.salary_sheet.date.year,
                ).aggregate(fine=Sum('total_late_attendance_fine'))
        return fine.get('fine', 0) if fine.get('fine') else 0.00
    get_late_fine.short_description = "Late Fine"

    def get_salary_loan(self, obj):
        salary_loan = obj.employee.loan_set.filter(
            start_date__lte=obj.salary_sheet.date,
            end_date__gte=obj.salary_sheet.date,
            loan_type="salary"
        )
        loan_amount = salary_loan.aggregate(Sum("emi"))

        return loan_amount["emi__sum"] if loan_amount["emi__sum"] else 0.0
    get_salary_loan.short_description = "Salary Loan"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser and not request.user.has_perm('account.can_see_salary_on_salary_sheet'):
            readonly_fields = [field for field in readonly_fields if field not in self.superadminonly_fields]
        return readonly_fields

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
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if not request.user.is_superuser and not request.user.has_perm('account.can_see_salary_on_salary_sheet') and 'total' in list_display:
            print(request.user, request.user.has_perm('account.can_see_salary_on_salary_sheet'))
            list_display.remove('total')
        return tuple(list_display)
    
    def total(self, obj):
        total_value = EmployeeSalary.objects.filter(salary_sheet_id=obj.id).aggregate(Sum('gross_salary'))[
            'gross_salary__sum']
        return format_html(
            f'<b>{intcomma(floor(total_value))}</b> <br>'
            f'{num2words(floor(total_value)).capitalize()}'
        )

    def total_employee(self, obj):
        return obj.employeesalary_set.count()
