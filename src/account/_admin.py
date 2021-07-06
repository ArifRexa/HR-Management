from datetime import datetime
from math import floor

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.humanize.templatetags.humanize import intcomma, intword
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.utils.html import format_html
from num2words import num2words
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from account.models import SalarySheet, EmployeeSalary, Expense, SalaryDisbursement
from account.repository.SalarySheetRepository import SalarySheetRepository
from employee.models import Employee


class EmployeeSalaryInline(admin.TabularInline):
    model = EmployeeSalary
    extra = 0
    readonly_fields = ('employee', 'net_salary', 'overtime',
                       'project_bonus', 'leave_bonus', 'festival_bonus', 'gross_salary')
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(SalarySheet)
class SalarySheetAdmin(admin.ModelAdmin):
    list_display = ('date', 'created_at', 'total', 'festival_bonus')
    fields = ('date', 'festival_bonus')
    inlines = (EmployeeSalaryInline,)
    actions = ('export_xl',)

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

    @admin.action(description='Export XL')
    def export_xl(self, request, queryset):
        wb = Workbook()
        work_sheets = {}
        for salary_sheet in queryset:
            salary_sheet.total_value = 0
            work_sheet = wb.create_sheet(title=str(salary_sheet.date))
            work_sheet.append(
                ['Name', 'Net Salary', 'Overtime', 'Project Bonus', 'Leave Bonus', 'Festival Bonus', 'Gross Salary',
                 'Bank Name', 'Bank Number'])
            for employee_salary in salary_sheet.employeesalary_set.all():
                salary_sheet.total_value += floor(employee_salary.gross_salary)
                bank_account = employee_salary.employee.bankaccount_set.filter(default=True).first()
                print(bank_account)
                work_sheet.append([
                    employee_salary.employee.full_name,
                    employee_salary.net_salary,
                    employee_salary.overtime,
                    employee_salary.project_bonus,
                    employee_salary.leave_bonus,
                    employee_salary.festival_bonus,
                    floor(employee_salary.gross_salary),
                    bank_account.bank.name if bank_account else '',
                    bank_account.account_number if bank_account else ''
                ])
                print(employee_salary)
            work_sheet.append(['', '', '', '', '', 'Total', salary_sheet.total_value])
            work_sheets[str(salary_sheet.id)] = work_sheet

        wb.remove(wb['Sheet'])
        response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=SalarySheet.xlsx'
        return response


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'amount', 'note', 'created_by')
    date_hierarchy = 'date'
    list_filter = ['created_by']
    change_list_template = 'admin/expense/list.html'

    def get_total_hour(self, request):
        filters = dict([(key, request.GET.get(key)) for key in dict(request.GET) if key not in ['p', 'o']])
        if not request.user.is_superuser:
            filters['created_by__id__exact'] = request.user.employee.id
        dataset = Expense.objects.filter(*[Q(**{key: value}) for key, value in filters.items() if value])
        return dataset.aggregate(tot=Sum('amount'))['tot']

    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super().changelist_view(request, extra_context=my_context)
    # TODO : Export to excel
    # TODO : Credit feature


class SalaryDisbursementForm(forms.ModelForm):
    employee = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(active=True).all(),
        widget=FilteredSelectMultiple("employee", is_stacked=False)
    )

    class Meta:
        model = SalaryDisbursement
        fields = '__all__'


@admin.register(SalaryDisbursement)
class SalaryDisbursementAdmin(admin.ModelAdmin):
    list_display = ('title', 'disbursement_type')
    form = SalaryDisbursementForm
