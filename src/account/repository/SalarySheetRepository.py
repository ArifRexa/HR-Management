import calendar
import time
from datetime import datetime, timedelta

from django.db.models import Sum

from account.models import SalarySheet, EmployeeSalary
from employee.models import Employee, SalaryHistory


class SalarySheetRepository:
    __total_payable = 0
    __salary_sheet = SalarySheet()
    __employee_current_salary = SalaryHistory()

    def __init__(self, date, festival_bonus=False):
        self.date = date
        self.festival_bonus = festival_bonus

    def save(self):
        """Generate and Save Salary Sheet

        @param date:
        @return:
        """
        salary_date = datetime.strptime(self.date, "%Y-%m-%d").date()
        self.__create_unique_sheet(salary_date)

    def __create_unique_sheet(self, salary_date: datetime.date):
        """Create unit salary sheet
        it will check if any salary sheet has been generated before on the given month
        it will update the salary sheet if found any
        otherwise it will create a new salary sheet of given date

        @type salary_date: datetime.date object
        """
        self.__salary_sheet, created = SalarySheet.objects.get_or_create(
            date__month=salary_date.month,
            date__year=salary_date.year,
            defaults={'date': salary_date}
        )
        self.__salary_sheet.festival_bonus = self.festival_bonus
        self.__salary_sheet.save()
        employees = Employee.objects.filter(
            active=True,
            joining_date__lte=salary_date
        ).exclude(salaryhistory__isnull=True)
        for employee in employees:
            self.__save_employee_salary(self.__salary_sheet, employee)

    def __save_employee_salary(self, salary_sheet: SalarySheet, employee: Employee):
        """Save Employee Salary to Salary sheet
        By this time will calculate the overtime, leave bonus, project bonus
        and make an addition with net salary

        @param salary_sheet:
        @param employee:
        @return void:
        """
        self.__employee_current_salary = employee.salaryhistory_set.filter(
            active_from__lte=salary_sheet.date.replace(day=1) - timedelta(days=1)
        ).last()
        employee_salary, created = EmployeeSalary.objects.get_or_create(
            employee=employee, salary_sheet=salary_sheet,
            defaults={'net_salary': 0, 'gross_salary': 0}
        )
        employee_salary.employee = employee
        employee_salary.salary_sheet = salary_sheet
        employee_salary.net_salary = self.__calculate_net_salary(salary_sheet, employee)
        employee_salary.overtime = self.__calculate_overtime(salary_sheet, employee)
        employee_salary.leave_bonus = self.__calculate_non_paid_leave(salary_sheet, employee)
        employee_salary.project_bonus = self.__calculate_project_bonus(salary_sheet, employee)
        employee_salary.festival_bonus = self.__calculate_festival_bonus(employee=employee)
        employee_salary.gross_salary = employee_salary.net_salary + employee_salary.overtime + \
                                       employee_salary.festival_bonus + \
                                       employee_salary.leave_bonus + employee_salary.project_bonus
        employee_salary.save()
        self.__total_payable += employee_salary.gross_salary

    def __calculate_net_salary(self, salary_sheet: SalarySheet, employee: Employee):
        """
        it will calculate the net salary of employee
        there is three kind of logic behind generating net salary
        1.if the employee join in the middle of the month
        2.if the employee left in the middle of the month
        3.if the employee has join and left in a same month of making salary sheet

        @param salary_sheet:
        @param employee:
        @return number:
        """
        working_days = calendar.monthrange(salary_sheet.date.year, salary_sheet.date.month)[1]
        joining_date = employee.joining_date.day
        resigned = employee.resignation_set.filter(status='approved', date__lte=salary_sheet.date).first()
        payable_days, working_days_after_join, working_days_after_resign = 0, 0, 0
        # if employee join at salary sheet making month
        if employee.joining_date.strftime('%Y-%m') == salary_sheet.date.strftime('%Y-%m'):
            working_days_after_join = (working_days + 1) - joining_date
        # if employee resigned at salary sheet making month
        if resigned:
            working_days_after_resign = working_days - (resigned.date.day - 1)
        # if employee join before salary month but resigned at the salarysheet making month
        if employee.joining_date.strftime('%Y-%m') < salary_sheet.date.strftime('%Y-%m') and resigned:
            working_days_after_join = working_days
        payable_days = working_days_after_join - working_days_after_resign

        # if employee join or leave or join and leave at salary sheet making month
        # print(f'Employee {employee.full_name} payable days : {payable_days}')
        latest_salary = self.__employee_current_salary
        if payable_days == 0:
            return latest_salary.payable_salary
        return (latest_salary.payable_salary / working_days) * payable_days

    def __calculate_overtime(self, salary_sheet: SalarySheet, employee: Employee):
        """Calculate Overtime
        If employee do overtime in salary sheet making month, and count the total number of overtime

        @param salary_sheet:
        @param employee:
        @return number:
        """
        return (self.__employee_current_salary.payable_salary / 15.5) * employee.overtime_set.filter(
            date__month=salary_sheet.date.month,
            date__year=salary_sheet.date.year,
            status='approved'
        ).count()

    def __calculate_non_paid_leave(self, salary_sheet: SalarySheet, employee: Employee):
        """Calculate Non Paid Leave
        it will calculate non paid leave if the employee tokes any
        it should always return negative integer

        @param salary_sheet:
        @param employee:
        @return negative number:
        """
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
        """Calculate Project Bonus
        this method will calculate project bonus if the employee is manager and the he is eligible for project bonus
        super admin will decide project hour is eligible or not for project bonus

        @param salary_sheet:
        @param employee:
        @return number:
        """
        project_hours = employee.projecthour_set.filter(
            date__month=salary_sheet.date.month,
            date__year=salary_sheet.date.year,
            payable=True
        ).aggregate(total_hour=Sum('hours'))['total_hour']
        if project_hours:
            return project_hours * 10
        return 0

    def __calculate_festival_bonus(self, employee: Employee):
        """Calculate festival bonus

        if this month have festival bonus and if the employee has joined more then
        180 days or 6 month from the salary_sheet making date he/she will applicable for festival bonus
        @param employee:
        @return number:
        """
        if self.festival_bonus:
            dtdelta = employee.joining_date + timedelta(days=180)
            if dtdelta < self.__salary_sheet.date:
                return (self.__employee_current_salary.payable_salary / 100) * employee.pay_scale.basic
        return 0
