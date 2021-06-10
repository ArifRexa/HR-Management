import time
from datetime import datetime

from account.models import SalarySheet, EmployeeSalary
from employee.models import Employee


class SalarySheetRepository:
    __total_payable = 0
    __salary_sheet = SalarySheet

    def save(self, date):
        salary_date = datetime.strptime(date, "%Y-%m-%d")
        self.__create_unique_sheet(salary_date)

    def __create_unique_sheet(self, salary_date: datetime):
        self.__salary_sheet, created = SalarySheet.objects.get_or_create(
            date__month=salary_date.month,
            date__year=salary_date.year,
            defaults={'date': salary_date}
        )
        employees = Employee.objects.all()
        for employee in employees:
            self.__save_employee_salary(self.__salary_sheet, employee)

    def __save_employee_salary(self, salary_sheet: SalarySheet, employee: Employee):
        salary_history = employee.salaryhistory_set.latest('id')
        employee_salary = EmployeeSalary()
        employee_salary.employee = employee
        employee_salary.salary_sheet = salary_sheet
        employee_salary.net_salary = salary_history.payable_salary
        employee_salary.overtime = self.__calculate_overtime(salary_sheet, employee)
        employee_salary.leave_bonus = 0
        employee_salary.gross_salary = employee.payable_salary + employee_salary.overtime + employee_salary.leave_bonus
        employee_salary.save()
        self.__total_payable += employee_salary.gross_salary

    def __calculate_overtime(self, salary_sheet: SalarySheet, employee: Employee):
        return (employee.payable_salary / 31) * employee.overtime_set.filter(
            date__month=salary_sheet.date.month,
            date__year=salary_sheet.date.year).count()
