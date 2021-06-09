from datetime import datetime
from django.contrib import admin
from account.models import SalarySheet, EmployeeSalary
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
    list_display = ('date', 'total_value', 'created_at')
    fields = ('date', 'total_value')
    inlines = (EmployeeSalaryInline,)
    readonly_fields = ('total_value',)

    def save_model(self, request, salary_sheet, form, change):
        salary_date = datetime.strptime(request.POST['date'], "%Y-%m-%d")
        super().save_model(request, salary_sheet, form, change)
        total = 0
        employees = Employee.objects.all()
        for employee in employees:
            employee_salary = self.__save_employee_salary(salary_sheet, employee)
            total += employee_salary.gross_salary
        self.__update_total_value(salary_sheet, total)

    def __save_employee_salary(self, salary_sheet, employee):
        employee_salary = EmployeeSalary()
        employee_salary.employee = employee
        employee_salary.salary_sheet = salary_sheet
        employee_salary.net_salary = employee.payable_salary
        employee_salary.overtime = self.__calculate_overtime(salary_sheet, employee)
        employee_salary.leave_bonus = 0
        employee_salary.gross_salary = employee.payable_salary + employee_salary.overtime + employee_salary.leave_bonus
        employee_salary.save()
        return employee_salary

    def __calculate_overtime(self, salary_sheet: SalarySheet, employee: Employee):
        return (employee.payable_salary / 31) * employee.overtime_set.filter(
            date__month=salary_sheet.date.month,
            date__year=salary_sheet.date.year).count()

    def __update_total_value(self, salary_sheet, total):
        sls = SalarySheet.objects.get(pk=salary_sheet.id)
        sls.total_value = total
        sls.save()
