import time
from datetime import datetime

from django.db.models import Sum

from account.models import SalarySheet, EmployeeSalary
from employee.models import Employee, SalaryHistory


class SalarySheetRepository:
    __total_payable = 0
    __salary_sheet = SalarySheet()
    __employee_current_salary = SalaryHistory()

    def save(self, date):
        salary_date = datetime.strptime(date, "%Y-%m-%d").date()
        self.__create_unique_sheet(salary_date)

    def __create_unique_sheet(self, salary_date: datetime.date):
        self.__salary_sheet, created = SalarySheet.objects.get_or_create(
            date__month=salary_date.month,
            date__year=salary_date.year,
            defaults={'date': salary_date}
        )
        print(EmployeeSalary.objects.filter(salary_sheet=self.__salary_sheet).delete())
        employees = Employee.objects.filter(active=True).exclude(salaryhistory__isnull=True)
        for employee in employees:
            self.__save_employee_salary(self.__salary_sheet, employee)

    def __save_employee_salary(self, salary_sheet: SalarySheet, employee: Employee):
        self.__employee_current_salary = employee.salaryhistory_set.latest('id')
        employee_salary = EmployeeSalary()
        employee_salary.employee = employee
        employee_salary.salary_sheet = salary_sheet
        employee_salary.net_salary = self.__calculate_net_salary(salary_sheet, employee)
        employee_salary.overtime = self.__calculate_overtime(salary_sheet, employee)
        employee_salary.leave_bonus = self.__calculate_non_paid_leave(salary_sheet, employee)
        employee_salary.project_bonus = self.__calculate_project_bonus(salary_sheet, employee)
        employee_salary.gross_salary = employee_salary.net_salary + employee_salary.overtime + \
                                       employee_salary.leave_bonus + employee_salary.leave_bonus
        employee_salary.save()
        self.__total_payable += employee_salary.gross_salary

    def __calculate_net_salary(self, salary_sheet: SalarySheet, employee: Employee):
        print(employee.full_name)
        delta = salary_sheet.date - employee.joining_date
        if delta.days < 30:
            return (self.__employee_current_salary.payable_salary / 30) * delta.days
        resigned = employee.resignation_set.filter(status='approved').first()
        if resigned:
            print('resigned last month' + employee.full_name)
            print(resigned.date.month == salary_sheet.date.month - 1)
            return 0
        return self.__employee_current_salary.payable_salary

    def __calculate_overtime(self, salary_sheet: SalarySheet, employee: Employee):
        return (self.__employee_current_salary.payable_salary / 31) * employee.overtime_set.filter(
            date__month=salary_sheet.date.month,
            date__year=salary_sheet.date.year).count()

    def __calculate_non_paid_leave(self, salary_sheet: SalarySheet, employee: Employee):
        total_non_paid_leave = employee.leave_set.filter(
            start_date__month=salary_sheet.date.month,
            start_date__year=salary_sheet.date.year,
            end_date__year=salary_sheet.date.year,
            end_date__month=salary_sheet.date.month,
            leave_type='non_paid',
            status='approved'
        ).aggregate(total_leave=Sum('total_leave'))['total_leave']
        if total_non_paid_leave:
            return -(self.__employee_current_salary.payable_salary / 31) * total_non_paid_leave
        return 0

    def __calculate_project_bonus(self, salary_sheet: SalarySheet, employee: Employee):
        project_hours = employee.projecthour_set.filter(
            date__month=salary_sheet.date.month,
            date__year=salary_sheet.date.year,
            payable=True
        ).aggregate(total_hour=Sum('hours'))['total_hour']
        if project_hours:
            return project_hours * 10
        return 0
