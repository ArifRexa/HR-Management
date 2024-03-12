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
from dateutil.relativedelta import relativedelta

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
            joining_date__lte=festival_bonus_date,
            festival_bonus_eligibility=True,
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

            If this month has a festival bonus and if the employee has joined more than
            180 days or 6 months from the salary_sheet making date, they will be applicable for the festival bonus.
            
            New policy effective from January 1, 2024:
            Employees joining before January 1, 2024, will follow the previous bonus policy.
            Employees joining from January 1, 2024, onwards will follow the new bonus policy.

            Additionally, for permanent employees (new policy):
            - Months 3-4: Bonus is 20% of basic salary
            - Months 5-6: Bonus is 40% of basic salary
            - Months 7-8: Bonus is 60% of basic salary
            - Months 9-10: Bonus is 80% of basic salary
            - Month 11: Bonus is 90% of basic salary
            - Month 12 and beyond: Bonus is 10% of basic salary
            
            @param employee: Employee object
            @return number: Festival bonus amount
            """
            
            
            # Determine the date for the previous and new policy cutoff
            previous_policy_cutoff = datetime(2024, 1, 1).date()
            new_policy_cutoff = self.__festival_bonus_sheet.date
            
            if employee.joining_date < previous_policy_cutoff:
               
                dtdelta = employee.joining_date + timedelta(days=180)
                seventyFivePercent = employee.joining_date + timedelta(days=150)
                fiftyPercent = employee.joining_date + timedelta(days=120)
                twinteeFivePercent = employee.joining_date + timedelta(days=90)
                tenPercent = employee.joining_date + timedelta(days=60)
                fivePercet = employee.joining_date + timedelta(days=30)
                
                basic_salary = (self.__employee_current_salary.payable_salary * 55) / 100
                
                if dtdelta < new_policy_cutoff:                
                    return basic_salary
                
                elif seventyFivePercent <= new_policy_cutoff: 
                    return round((basic_salary * 75) / 100, 2)
                
                elif fiftyPercent <= new_policy_cutoff:
                    return round((basic_salary * 50) / 100, 2)
                
                elif twinteeFivePercent <= new_policy_cutoff:
                    return round((basic_salary * 25) / 100, 2)
                
                elif tenPercent <= new_policy_cutoff:
                    return round((basic_salary * 10) / 100, 2)
                
                elif fivePercet <= new_policy_cutoff:
                    return round((basic_salary * 5) / 100, 2)
                
            else:
               
                if employee.permanent_date:
                   
                    joining_date = employee.joining_date
                    festival_bonus_date = self.__festival_bonus_sheet.date

                    # Calculate the difference in years using relativedelta
                    delta = relativedelta(festival_bonus_date, joining_date)

                    # Calculate the total months since joining
                    months_since_joining = delta.years * 12 + delta.months
                    print(months_since_joining)
                   
                    # Calculate festival bonus based on months since joining
                    basic_salary = (self.__employee_current_salary.payable_salary * 55) / 100
                    if months_since_joining < 3:
                        return 0
                    elif months_since_joining >= 3 and months_since_joining < 5:
                        return round((basic_salary * 20) / 100, 2)
                    elif months_since_joining >= 5 and months_since_joining < 7:
                        return round((basic_salary * 40) / 100, 2)
                    elif months_since_joining >= 7 and months_since_joining < 9:
                        return round((basic_salary * 60) / 100, 2)
                    elif months_since_joining >= 9 and months_since_joining < 11:
                        return round((basic_salary * 80) / 100, 2)
                    elif months_since_joining == 11:
                        return round((basic_salary * 90) / 100, 2)
                    elif months_since_joining >= 12:
                        return round((basic_salary * 100) / 100, 2)
                else:
                    
                    return 0