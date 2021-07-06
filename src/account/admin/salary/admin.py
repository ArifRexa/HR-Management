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
    readonly_fields = ('employee', 'net_salary', 'overtime',
                       'project_bonus', 'leave_bonus', 'festival_bonus', 'gross_salary')
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(SalarySheet)
class SalarySheetAdmin(SalarySheetAction, admin.ModelAdmin):
    list_display = ('date', 'created_at', 'total', 'festival_bonus')
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

    # @admin.action(description='Export XL')
    # def export_xl(self, request, queryset):
    #     wb = Workbook()
    #     work_sheets = {}
    #     for salary_sheet in queryset:
    #         salary_sheet.total_value = 0
    #         work_sheet = wb.create_sheet(title=str(salary_sheet.date))
    #         work_sheet.append(
    #             ['Name', 'Net Salary', 'Overtime', 'Project Bonus', 'Leave Bonus', 'Festival Bonus', 'Gross Salary',
    #              'Bank Name', 'Bank Number'])
    #         for employee_salary in salary_sheet.employeesalary_set.all():
    #             salary_sheet.total_value += floor(employee_salary.gross_salary)
    #             bank_account = employee_salary.employee.bankaccount_set.filter(default=True).first()
    #             print(bank_account)
    #             work_sheet.append([
    #                 employee_salary.employee.full_name,
    #                 employee_salary.net_salary,
    #                 employee_salary.overtime,
    #                 employee_salary.project_bonus,
    #                 employee_salary.leave_bonus,
    #                 employee_salary.festival_bonus,
    #                 floor(employee_salary.gross_salary),
    #                 bank_account.bank.name if bank_account else '',
    #                 bank_account.account_number if bank_account else ''
    #             ])
    #             print(employee_salary)
    #         work_sheet.append(['', '', '', '', '', 'Total', salary_sheet.total_value])
    #         work_sheets[str(salary_sheet.id)] = work_sheet
    #
    #     wb.remove(wb['Sheet'])
    #     response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/ms-excel')
    #     response['Content-Disposition'] = 'attachment; filename=SalarySheet.xlsx'
    #     return response
