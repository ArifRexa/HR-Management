import os
import calendar
from datetime import datetime, timedelta

from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.utils import timezone

from account.models import FestivalBonusSheet, EmployeeFestivalBonus, LoanPayment
from employee.models import Employee, SalaryHistory, Leave, Overtime, EmployeeAttendance
from project_management.models import EmployeeProjectHour, ProjectHour
from settings.models import PublicHolidayDate
from django.db.models import Count, Sum, Avg
from employee.models.config import Config
from project_management.models import CodeReview


class FestivalBonusSheetRepository:
    __total_payable = 0
    __festival_bonus_sheet = FestivalBonusSheet()
    __employee_current_salary = SalaryHistory()

    def __init__(self, date):
        self.date = date

    def save(self):
        """Generate and Save Salary Sheet

        @param date:
        @return:
        """
        festival_bonus_date = datetime.strptime(self.date, "%Y-%m-%d").date()
        self.__create_unique_sheet(festival_bonus_date)

    def __create_unique_sheet(self, festival_bonus_date: datetime.date):
        """Create unit bonus sheet
        it will check if any bonus sheet has been generated before on the given month
        it will update the bonus sheet if found any
        otherwise it will create a new bonus sheet of given date

        @type festival_bonus_date: datetime.date object
        """
        self.__festival_bonus_sheet, created = FestivalBonusSheet.objects.get_or_create(
            date__month=festival_bonus_date.month,
            date__year=festival_bonus_date.year,
            defaults={'date': festival_bonus_date}
        )
        self.__festival_bonus_sheet.save()
        employees = Employee.objects.filter(
            active=True,
            joining_date__lte=festival_bonus_date
        ).exclude(salaryhistory__isnull=True)
        for employee in employees:
            self.__save_employee_festival_bonus(self.__festival_bonus_sheet, employee)

    def __save_employee_festival_bonus(self, festival_bonus_sheet: FestivalBonusSheet, employee: Employee):
        """Save Employee Festival Bonus to Festival Bonus sheet

        @param festival_bonus_sheet:
        @param employee:
        @return void:
        """

        self.__employee_current_salary = employee.salaryhistory_set.filter(
            active_from__lte=festival_bonus_sheet.date.replace(day=1)
        ).last()
        if self.__employee_current_salary is None:
            self.__employee_current_salary = employee.current_salary
        employee_salary, created = EmployeeFestivalBonus.objects.get_or_create(
            employee=employee, 
            festival_bonus_sheet=festival_bonus_sheet,
        )

        employee_salary.employee = employee
        employee_salary.festival_bonus_sheet = festival_bonus_sheet
        
        employee_salary.amount = self.__calculate_festival_bonus(
            employee=employee,
        )
        employee_salary.save()

        self.__total_payable += employee_salary.amount

    def __calculate_festival_bonus(self, employee: Employee):
        """Calculate festival bonus

        If this month has a festival bonus and the employee has joined more than 
        
        180 days or 6 months from the salary sheet making date, he or she will be eligible for a 100% festival bonus

        150 days or 5 months from the salary sheet making date, he or she will be eligible for a 75% festival bonus

        120 days or 4 months from the salary sheet making date, he or she will be eligible for a 50% festival bonus

        90 days or 3 months from the salary sheet making date, he or she will be eligible for a 25% festival bonus

        60 days or 2 months from the salary sheet making date, he or she will be eligible for a 10% festival bonus

        30 days or 1 months from the salary sheet making date, he or she will be eligible for a 5% festival bonus

        @param employee:
        @return number: The calculated festival bonus
        """
        dtdelta = employee.joining_date + timedelta(days=180)
        seventyFivePercent = employee.joining_date + timedelta(days=150)
        fiftyPercent = employee.joining_date + timedelta(days=120)
        twinteeFivePercent = employee.joining_date + timedelta(days=90)
        tenPercent = employee.joining_date + timedelta(days=60)
        fivePercet = employee.joining_date + timedelta(days=30)
        
        basic_salary = (self.__employee_current_salary.payable_salary / 100) * employee.pay_scale.basic

        if dtdelta < self.__festival_bonus_sheet.date:
            return basic_salary
        elif seventyFivePercent <= self.__festival_bonus_sheet.date:
            return round((basic_salary * 75) / 100 , 2)
        elif fiftyPercent <= self.__festival_bonus_sheet.date:
            return round((basic_salary * 50) / 100 , 2)
        elif twinteeFivePercent <= self.__festival_bonus_sheet.date:
            return round((basic_salary * 25) / 100 , 2)
        elif tenPercent <= self.__festival_bonus_sheet.date:
            return round((basic_salary * 10) / 100 , 2)
        elif fivePercet <= self.__festival_bonus_sheet.date:
            return round((basic_salary * 5) / 100 , 2)
        
        return 0

