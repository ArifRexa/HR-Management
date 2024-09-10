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
from decimal import Decimal
from django.db.models import Count

from employee.templatetags.employee_helper import total_employee_count

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
            start_date__month=obj.salary_sheet.date.month,
            end_date__year=obj.salary_sheet.date.year,
            loan_type="salary"
        )
        loan_amount = salary_loan.aggregate(Sum("loan_amount"))
        return -loan_amount["loan_amount__sum"] if loan_amount["loan_amount__sum"] else 0.0
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
    
     

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Filter by the current SalarySheet
        salary_sheet_id = self.parent_model.objects.filter(id=request.resolver_match.kwargs.get('object_id')).values_list('id', flat=True).first()
        qs = qs.filter(salary_sheet_id=salary_sheet_id)
        
        # Calculate totals
        self.total_values = qs.aggregate(
            total_employees = Count('id'),
            total_net_salary=Sum('net_salary'),
            total_overtime=Sum('overtime'),
            total_project_bonus=Sum('project_bonus'),
            total_leave_bonus=Sum('leave_bonus'),
            total_food_allowance=Sum('food_allowance'),
            total_festival_bonus=Sum('festival_bonus'),
            total_gross_salary=Sum('gross_salary'),
        )
        
        # Initialize total_late_fine as Decimal
        total_late_fine = Decimal('0.00')
        total_tax_loan = Decimal('0.00')
        total_salary_loan = Decimal('0.00')

        # Calculate custom total for late fines manually
        for obj in qs:
            total_late_fine += Decimal(self.get_late_fine(obj))
            total_tax_loan += Decimal(self.get_tax_loan(obj))
            total_salary_loan+= Decimal(self.get_salary_loan(obj))
        
        self.total_values['total_late_fine'] = total_late_fine
        self.total_values['total_tax_loan'] = -total_tax_loan
        self.total_values['total_salary_loan'] = -total_salary_loan

        return qs
@admin.register(SalarySheet)
class SalarySheetAdmin(SalarySheetAction, admin.ModelAdmin):
    list_display = ('date', 'created_at', 'total', 'total_employee', 'festival_bonus')
    fields = ('date', 'festival_bonus')
    inlines = (EmployeeSalaryInline,)
    change_form_template = ('admin/salary_sheet.html')
    

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
    
 # Override change_view to pass the calculated totals to the template
    def change_view(self, request, object_id, form_url='', extra_context=None):
        salary_sheet = self.get_object(request, object_id)
        inline_instance = self.get_inline_instances(request, salary_sheet)[0]
        inline_instance_queryset = inline_instance.get_queryset(request)

        # Add total values from EmployeeSalaryInline to the context
        extra_context = extra_context or {}
        extra_context['total_values'] = inline_instance.total_values

        return super().change_view(request, object_id, form_url, extra_context=extra_context)