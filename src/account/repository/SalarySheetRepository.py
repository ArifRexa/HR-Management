import calendar
from datetime import datetime, timedelta
from collections import defaultdict

from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.utils import timezone

from account.models import SalarySheet, EmployeeSalary, LoanPayment
from employee.models import Employee, SalaryHistory, Leave, Overtime, EmployeeAttendance
from project_management.models import EmployeeProjectHour, ProjectHour
from settings.models import PublicHolidayDate
from django.db.models import Count, Sum, Avg
from employee.models.config import Config
from project_management.models import CodeReview


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
            active_from__lte=salary_sheet.date.replace(day=1)
        ).last()
        if self.__employee_current_salary is None:
            self.__employee_current_salary = employee.current_salary
        employee_salary, created = EmployeeSalary.objects.get_or_create(
            employee=employee, salary_sheet=salary_sheet,
            defaults={'net_salary': 0, 'gross_salary': 0}
        )
        employee_salary.employee = employee
        employee_salary.salary_sheet = salary_sheet
        employee_salary.net_salary = self.__calculate_net_salary(
            salary_sheet, employee)
        employee_salary.overtime = self.__calculate_overtime(
            salary_sheet, employee)
        employee_salary.leave_bonus = self.__calculate_non_paid_leave(salary_sheet, employee) + \
            self.__calculate_leave_in_cash(salary_sheet, employee)
        employee_salary.project_bonus = self.__calculate_project_bonus(
            salary_sheet, employee)
        employee_salary.code_quality_bonus = self.__calculate_code_quality_bonus(
            salary_sheet, employee)
        employee_salary.festival_bonus = self.__calculate_festival_bonus(
            employee=employee)
        employee_salary.food_allowance = self.__calculate_food_allowance(employee=employee,
                                                                         salary_date=salary_sheet.date)
        employee_salary.device_allowance = self.__calculate_device_allowance(
            employee=employee,
            salary_date=salary_sheet.date
        )
        employee_salary.loan_emi = self.__calculate_loan_emi(
            employee=employee, salary_date=salary_sheet.date)
        employee_salary.provident_fund = self.__calculate_provident_fund(
            employee=employee, salary_date=salary_sheet.date)
        employee_salary.gross_salary = employee_salary.net_salary + employee_salary.overtime + \
            employee_salary.festival_bonus + employee_salary.food_allowance + \
            employee_salary.leave_bonus + employee_salary.project_bonus + \
            employee_salary.code_quality_bonus + employee_salary.loan_emi + \
            employee_salary.provident_fund + employee_salary.device_allowance
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
        working_days = calendar.monthrange(
            salary_sheet.date.year, salary_sheet.date.month)[1]
        joining_date = employee.joining_date.day
        resigned = employee.resignation_set.filter(
            status='approved', date__lte=salary_sheet.date).first()
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

        # 31 / 1.5
        return (self.__employee_current_salary.payable_salary / 20.67) * employee.overtime_set.filter(
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

    def __calculate_leave_in_cash(self, salary_sheet: SalarySheet, employee: Employee):
        """Calculate Leave in Cash
        It will only effect at end of the year which is December
        The % of the in case will come from the pay scale
        it should always return number

        @param employee:
        @param salary_sheet:
        @return:
        """
        leave_in_cash = 0
        if salary_sheet.date.month == 12 and employee.leave_in_cash_eligibility and employee.permanent_date != None:
            one_day_salary = self.__employee_current_salary.payable_salary / 31
            payable_medical_leave = employee.leave_available_leaveincash('medical_leave', salary_sheet.date) - \
                employee.leave_passed('medical', salary_sheet.date.year)
            payable_medical_leave_amount = ((payable_medical_leave * employee.pay_scale.leave_in_cash_medical) / 100) \
                * one_day_salary

            payable_casual_leave = employee.leave_available_leaveincash('casual_leave', salary_sheet.date) - \
                employee.leave_passed('casual', salary_sheet.date.year)
            payable_casual_leave_amount = ((payable_casual_leave * employee.pay_scale.leave_in_cash_casual) / 100) \
                * one_day_salary

            leave_in_cash = payable_medical_leave_amount + payable_casual_leave_amount

            # INLINE DEBUG
            # print("="*30)
            # print()
            # print("", self.__employee_current_salary.payable_salary)
            # print("One day Salary: ", )
            # print("Medical Cash:", )
            # print("Casual Cash:", )
            # print("Payable Medial:", )
            # print("Payable Casual:", )
            # print("Leave Cash:", leave_in_cash)
            # print("="*30)

            # text = f"""Employee: {employee.full_name}

            # Payable Salary: {one_day_salary}

            # Medical Cash: {employee.pay_scale.leave_in_cash_medical}
            # Casual Cash: {employee.pay_scale.leave_in_cash_casual}

            # Payable Medial: {payable_medical_leave}
            # Payable Casual: {payable_casual_leave}

            # Leave Cash: {leave_in_cash}"""

            # file_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) + '/media/temp_emp_salary'

            # if not os.path.exists(file_dir):
            #     os.mkdir(file_dir)

            # with open(f'{file_dir}/{employee.id}.txt', 'w') as f:
            #     f.write(text)
            # INLINE DEBUG

        return leave_in_cash

    def __calculate_project_bonus(self, salary_sheet: SalarySheet, employee: Employee):
        """Calculate Project Bonus
        this method will calculate project bonus if the employee is manager and the he is eligible for project bonus
        super admin will decide project hour is eligible or not for project bonus

        @param salary_sheet:
        @param employee:
        @return number:
        """

        project_hours = employee.employeeprojecthour_set.filter(
            project_hour__date__month=salary_sheet.date.month,
            project_hour__date__year=salary_sheet.date.year
        ).aggregate(total_hour=Coalesce(Sum('hours'), 0.0))['total_hour']

        # if (
        #     employee.manager 
        #     or employee.lead
        # ):
        project_hours += employee.projecthour_set.filter(
            date__month=salary_sheet.date.month,
            date__year=salary_sheet.date.year,
            payable=True
        ).aggregate(total_hour=Coalesce(Sum('hours'), 0.0))['total_hour']
        
        # Hour Bonus Amount Calculation
        project_hours_amount = 0
        if (
            employee.manager 
            or employee.lead
        ):
            project_hours_amount = project_hours * 13
        else:
            MAXIMUM_AMOUNT = 16
            bonus_per_hour = defaultdict(lambda: MAXIMUM_AMOUNT, {
                **dict.fromkeys(range(0, 100), 10),
                **dict.fromkeys(range(100, 120), 13),
            })
            project_hours_amount = project_hours * bonus_per_hour[round(project_hours)]
        
        return project_hours_amount

    def __calculate_code_quality_bonus(self, salary_sheet: SalarySheet, employee: Employee):
        _, last_day = calendar.monthrange(
            salary_sheet.date.year, salary_sheet.date.month)
        qc_total_point = 0
        if employee.manager:
            reviews_avg = CodeReview.objects.filter(
                manager=employee,
                created_at__month=salary_sheet.date.month,
                created_at__year=salary_sheet.date.year,
            ).values('employee').annotate(Sum('avg_rating'), Count('id'))
            total_point = 0
            for review in reviews_avg:
                total_point += review.get('avg_rating__sum') / \
                    review.get('id__count') / 2

            qc_total_point += total_point

        qc_total_point += employee.codereview_set.filter(
            created_at__month=salary_sheet.date.month,
            created_at__year=salary_sheet.date.year,
        ).aggregate(avg=Coalesce(Avg('avg_rating'), 0.0)).get("avg")

        # first_quarter = code_review_set.filter(created_at__day__lte=15).exists()
        # second_quarter = code_review_set.filter(created_at__day__gte=16).exists()

        # if first_quarter and second_quarter:

        qc_ratio = Config.objects.first().qc_bonus_amount
        ratio = qc_ratio if qc_ratio else 0

        return round(qc_total_point * ratio, 2)

    def __calculate_festival_bonus(self, employee: Employee):
        """Calculate festival bonus

        if this month have festival bonus and if the employee has joined more then
        180 days or 6 month from the salary_sheet making date he/she will applicable for festival bonus
        @param employee:
        @return number:
        """
        if self.festival_bonus:
            dtdelta = employee.joining_date + timedelta(days=180)
            seventyFivePercent = employee.joining_date + timedelta(days=150)
            fiftyPercent = employee.joining_date + timedelta(days=120)
            twinteeFivePercent = employee.joining_date + timedelta(days=90)
            tenPercent = employee.joining_date + timedelta(days=60)
            fivePercet = employee.joining_date + timedelta(days=30)
            
            basic_salary = (self.__employee_current_salary.payable_salary / 100) * employee.pay_scale.basic
            if dtdelta < self.__salary_sheet.date:
                return basic_salary
            elif seventyFivePercent <= self.__salary_sheet.date:
                return round((basic_salary * 75) / 100 , 2)
            elif fiftyPercent <= self.__salary_sheet.date:
                return round((basic_salary * 50) / 100 , 2)
            elif twinteeFivePercent <= self.__salary_sheet.date:
                return round((basic_salary * 25) / 100 , 2)
            elif tenPercent <= self.__salary_sheet.date:
                return round((basic_salary * 10) / 100 , 2)
            elif fivePercet <= self.__salary_sheet.date:
                return round((basic_salary * 5) / 100 , 2)
        return 0

    def __calculate_loan_emi(self, employee: Employee, salary_date: datetime.date):
        """Calculate loan EMI if have any

        if the employee have loan and the loan does not finish it will sum all the loan emi amount
        """
        employee_loans = employee.loan_set.filter(
            start_date__lte=salary_date,
            end_date__gte=salary_date,
        )
        # insert into loan payment table if the sum amount is not zero
        for employee_loan in employee_loans:
            note = f'This payment has been made automated when salary sheet generated at {salary_date}'
            employee_loan.loanpayment_set.get_or_create(
                loan=employee_loan, payment_amount=employee_loan.emi,
                note=note, payment_date=salary_date,
                defaults={'payment_date': salary_date, 'loan': employee_loan}
            )
        emi_amount = employee_loans.aggregate(Sum('emi'))
        return -emi_amount['emi__sum'] if emi_amount['emi__sum'] else 0.0

    def __calculate_provident_fund(self, employee: Employee, salary_date: datetime.date):
        """Calculate provident fund amount if have any
        """
        return 0.0
        if not employee.pf_eligibility:
            return 0.0

        pf_account = employee.pf_account
        monthly_amount = 0
        note = f'This payment has been made automated when salary sheet generated at {salary_date}'
        basic_salary = (employee.pay_scale.basic *
                        self.__employee_current_salary.payable_salary) / 100
        monthly_amount = (basic_salary * pf_account.scale) / 100

        monthly_entry = employee.pf_account.monthlyentry_set.create(
            tranx_date=salary_date,
            amount=monthly_amount,
            basic_salary=basic_salary,
            note=note,
        )

        return -monthly_amount if monthly_amount else 0.0

    def __calculate_food_allowance(self, employee: Employee, salary_date: datetime.date):
        if not employee.lunch_allowance:
            return 0.0
        # date_range = calendar.monthrange(salary_date.year, salary_date.month)
        # import datetime

        # # TODO: Fix for resign date
        # if employee.joining_date.year == salary_date.year and employee.joining_date.month == salary_date.month:
        #     start_date = datetime.date(salary_date.year, salary_date.month, employee.joining_date.day)
        # else:
        #     start_date = datetime.date(salary_date.year, salary_date.month, 1)

        # end_date = datetime.date(salary_date.year, salary_date.month, date_range[1])
        # office_holidays = PublicHolidayDate.objects.filter(date__gte=start_date,
        #                                                    date__lte=end_date).values_list('date', flat=True)

        # # TODO: What if leave spans to next month
        # employee_on_leave = Leave.objects.filter(
        #     start_date__month=salary_date.month,
        #     start_date__year=salary_date.year,
        #     end_date__year=salary_date.year,
        #     end_date__month=salary_date.month,
        #     status='approved',
        #     employee=employee).aggregate(total_leave=Coalesce(Sum('total_leave'), 0.0))['total_leave']

        # # employee_overtime = Overtime.objects.filter(date__gte=start_date, date__lte=end_date, status='approved',
        # #                                          employee=employee).aggregate(total=Coalesce(Count('id'), 0))['total']

        # # TODO: Temporary fix
        # employee_overtime = 0
        # if Overtime.objects.filter(date=datetime.date(2022, 12, 16), status='approved', employee=employee).exists() or employee.permanent_date:
        #     employee_overtime = 1

        # # print(employee, employee_on_leave)
        # day_off = 0
        # for day in range(start_date.day, date_range[1] + 1):
        #     date = datetime.date(salary_date.year, salary_date.month, day)
        #     if date.strftime("%A") in ['Saturday', 'Sunday']:
        #         day_off += 1
        #     if date in office_holidays:
        #         day_off += 1
        # day_off += employee_on_leave
        # payable_days = (date_range[1] - start_date.day) - day_off + employee_overtime
        skipp_days = Config.objects.first().skip_lunch_amount
        payable_days = EmployeeAttendance.objects.filter(
            employee=employee,
            date__year=salary_date.year,
            date__month=salary_date.month,
        ).aggregate(total=Coalesce(Count('id'), 0))['total']
        total_allowance = (payable_days - skipp_days) * 140
        return max(total_allowance, 0)
    

    def __calculate_device_allowance(self, employee: Employee, salary_date: datetime.date):
        return 3000.0 if employee.device_allowance else 0.0

