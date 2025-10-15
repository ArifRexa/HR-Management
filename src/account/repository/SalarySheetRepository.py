import calendar
from decimal import Decimal
import math
from datetime import datetime, timedelta


from django.db.models import Sum, Count, DecimalField, Value, Q, Case, FloatField, When, F
from django.db.models.functions import Coalesce

from django.utils import timezone

from account.models import (
    InvestmentAllowance,
    SalarySheet,
    EmployeeSalary,
    Loan,
    SalarySheetTaxLoan,
    VehicleRebate,
)
from employee.models import Employee, SalaryHistory
from employee.models.employee import LateAttendanceFine
# from settings.models import EmployeeFoodAllowance
from django.db.models import Avg
from employee.models.config import Config
from project_management.models import CodeReview
from dateutil.relativedelta import relativedelta


def get_fiscal_year_dates(start_month=7):
    date = datetime.now()
    year = date.year
    if date.month < start_month:
        start_year = year - 1
    else:
        start_year = year

    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(start_year + 1, start_month, 1) - timedelta(days=1)

    return start_date, end_date


class EmployeeTaxLoanRepository:
    __salary_sheet = SalarySheet()
    __employee_current_salary = SalaryHistory()

    def __init__(self, employee: Employee, date):
        self.date = date
        self.salary_date = datetime.strptime(self.date, "%Y-%m-%d").date()
        self.salary_sheet = self.__salary_sheet
        self.__salary_sheet, created = SalarySheet.objects.get_or_create(
            date__month=self.salary_date.month,
            date__year=self.salary_date.year,
            defaults={"date": self.salary_date},
        )
        self.employee = employee
        self.__employee_current_salary = employee.salaryhistory_set.filter(
            active_from__lte=self.__salary_sheet.date.replace(day=1)
        ).last()
        if self.__employee_current_salary is None:
            self.__employee_current_salary = self.employee.current_salary
        self.monthly_pay_amount = self.__employee_current_salary.payable_salary
        self.fiscal_start_date, self.fiscal_end_date = (
            get_fiscal_year_dates()
        )  # default 7th month if need adjust

    def calculate_tax_loan(self):
        taxable_income = self.get_yearly_gross_income() - self.get_exemption()
        tax_eligible_amount = {
            "male": 350000,
            "female": 400000,
        }
        if taxable_income <= tax_eligible_amount.get(self.employee.gender, 0):
            return 0
        vehicle_or_other_paid_tax = self.get_tax_for_vehicle()
        tax = Decimal(self.calculate_income_tax(taxable_income))
        rebate = self.get_investment_rebate()
        if rebate > 0:
            tax -= Decimal(rebate)
        if vehicle_or_other_paid_tax and tax < vehicle_or_other_paid_tax:
            return 0
        elif vehicle_or_other_paid_tax and tax > vehicle_or_other_paid_tax:
            tax -= vehicle_or_other_paid_tax
            return math.ceil(tax / 12)

        yearly_tax = 5000 if tax <= 5000 else tax
        return math.ceil(yearly_tax / 12)

    def calculate_income_tax(self, income):
        # Tax brackets and their corresponding rates

        brackets = [
            (350000, 0.00),
            (100000, 0.05),
            (400000, 0.10),
            (500000, 0.15),
            (500000, 0.15),
            (2000000, 0.25),
        ]

        female_brackets = [
            (400000, 0.00),
            (100000, 0.05),
            (400000, 0.10),
            (500000, 0.15),
            (500000, 0.15),
            (2000000, 0.25)
        ]
        if self.employee.gender == "female":
            brackets = female_brackets

        # Start with no tax
        tax = 0

        for bracket, rate in brackets:
            if income > bracket:
                tax += bracket * rate
                income -= bracket
            else:
                tax += income * rate
                return tax

        # If there's any remaining income above the last bracket
        if income:
            tax += income * 0.30

        return tax

    def get_yearly_gross_income(self):
        """
        Calculate yearly gross income
        gross_income = monthly_gross * 12 + 2 * festival_bonus
        """
        festival_bonus = self.monthly_pay_amount * 0.55
        # gross_income = (self.monthly_pay_amount * 12) + 2 * (self.get_festival_bonus())
        gross_income = (self.monthly_pay_amount * 12) + 2 * festival_bonus
        return gross_income

    def get_exemption(self):
        one_third = self.get_yearly_gross_income() / 3
        return min(one_third, 450000)

    def get_festival_bonus(self):
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
        # if festival_bonus:
        # Determine the date for the previous and new policy cutoff
        previous_policy_cutoff = datetime(2024, 1, 1).date()
        new_policy_cutoff = self.__salary_sheet.date

        if self.employee.joining_date < previous_policy_cutoff:
            if self.employee.permanent_date:
                # Apply previous policy
                dtdelta = self.employee.joining_date + timedelta(days=180)
                seventyFivePercent = self.employee.joining_date + timedelta(days=150)
                fiftyPercent = self.employee.joining_date + timedelta(days=120)
                twinteeFivePercent = self.employee.joining_date + timedelta(days=90)
                tenPercent = self.employee.joining_date + timedelta(days=60)
                fivePercet = self.employee.joining_date + timedelta(days=30)

                basic_salary = (
                    self.__employee_current_salary.payable_salary * 55
                ) / 100

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
                return 0

        else:
            if self.employee.permanent_date:
                joining_date = self.employee.joining_date
                festival_bonus_date = self.__salary_sheet.date

                # Calculate the difference in years using relativedelta
                # full = employee.joining_date + timedelta(days=360)
                # ninety_percent = employee.joining_date + timedelta(days=330)
                # eighty_percent = employee.joining_date + timedelta(days=270)
                # sixty_percent = employee.joining_date + timedelta(days=210)
                # fourty_percent = employee.joining_date + timedelta(days=150)
                # twintee_percent = employee.joining_date + timedelta(days=90)

                delta = relativedelta(festival_bonus_date, joining_date)

                # Calculate the total months since joining
                months_since_joining = delta.years * 12 + delta.months
                days_since_joining = (
                    (delta.years * 12 + delta.months) * 30
                ) + delta.days
                print(self.employee, months_since_joining)

                basic_salary = (
                    self.__employee_current_salary.payable_salary * 55
                ) / 100

                if days_since_joining < 90:
                    return 0
                elif days_since_joining >= 90 and days_since_joining < 150:
                    return round((basic_salary * 20) / 100, 2)
                elif days_since_joining >= 150 and days_since_joining < 210:
                    return round((basic_salary * 40) / 100, 2)
                elif days_since_joining >= 210 and days_since_joining < 270:
                    return round((basic_salary * 60) / 100, 2)
                elif days_since_joining >= 270 and days_since_joining < 330:
                    return round((basic_salary * 80) / 100, 2)
                elif days_since_joining >= 330 and days_since_joining < 360:
                    return round((basic_salary * 90) / 100, 2)
                else:
                    return basic_salary

                # if festival_bonus_date < twintee_percent:
                #     return 0
                # elif twintee_percent >= festival_bonus_date  and fourty_percent < festival_bonus_date:
                #     return round((basic_salary * 20) / 100, 2)
                # elif fourty_percent >= festival_bonus_date  and sixty_percent < festival_bonus_date:
                #     return round((basic_salary * 40) / 100, 2)
                # elif sixty_percent >= festival_bonus_date  and eighty_percent < festival_bonus_date:
                #     return round((basic_salary * 60) / 100, 2)
                # elif eighty_percent >= new_policy_cutoff  and ninety_percent < festival_bonus_date:
                #     return round((basic_salary * 80) / 100, 2)
                # elif ninety_percent >= festival_bonus_date:
                #     return round((basic_salary * 90) / 100, 2)
                # elif full >= festival_bonus_date:
                #     return round((basic_salary * 100) / 100, 2)
            else:
                return 0

        return 0

    def get_investment_rebate(self):
        """
        A. 15% of Actual Investment
        B. 3% of net taxable income*
        C. Maximum Limit = 1000000
        Allowable investment Allowance (Lower of A, B & C)
        """
        total_investment = InvestmentAllowance.objects.filter(
            employee=self.employee,
            created_at__date__gte=self.fiscal_start_date,
            created_at__date__lte=self.fiscal_end_date,
        ).aggregate(
            total_allowance=Coalesce(
                Sum("amount"), Value(0.0), output_field=DecimalField()
            )
        )
        percentage_actual_invest = total_investment.get("total_allowance", 0) * Decimal(
            0.15
        )
        percentage_net_taxable_income = (
            self.get_yearly_gross_income() - self.get_exemption()
        ) * 0.03
        return min([percentage_actual_invest, percentage_net_taxable_income, 1000000])

    def get_tax_for_vehicle(self):
        total = VehicleRebate.objects.filter(
            employee=self.employee,
            created_at__date__gte=self.fiscal_start_date,
            created_at__date__lte=self.fiscal_end_date,
        ).aggregate(
            total_rebate=Coalesce(Sum("amount"), Value(0), output_field=DecimalField())
        )
        return total.get("total_rebate", 0)


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
            defaults={"date": salary_date},
        )
        self.__salary_sheet.festival_bonus = self.festival_bonus
        self.__salary_sheet.save()

        # generate all eligible employee for salary
        employees = Employee.objects.filter(
            active=True, joining_date__lte=salary_date
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
            employee=employee,
            salary_sheet=salary_sheet,
            defaults={"net_salary": 0, "gross_salary": 0},
        )
        employee_salary.employee = employee
        employee_salary.salary_sheet = salary_sheet
        employee_salary.net_salary = self.__calculate_net_salary(salary_sheet, employee)
        employee_salary.overtime = self.__calculate_overtime(salary_sheet, employee)
        employee_salary.leave_bonus = (
            self.__calculate_non_paid_leave(salary_sheet, employee)
            + self.__calculate_leave_in_cash(salary_sheet, employee)
            + self.__resignation_employee_non_paid_leave(salary_sheet, employee)
        )
        employee_salary.project_bonus = self.__calculate_project_bonus(
            salary_sheet, employee
        )
        employee_salary.code_quality_bonus = self.__calculate_code_quality_bonus(
            salary_sheet, employee
        )
        employee_salary.festival_bonus = self.__calculate_festival_bonus(
            employee=employee
        )
        employee_salary.food_allowance = self.__calculate_food_allowance(
            employee=employee, salary_date=salary_sheet.date
        )
        employee_salary.device_allowance = self.__calculate_device_allowance(
            employee=employee, salary_date=salary_sheet.date
        )

        # employee_salary.loan_emi = self.__calculate_loan_emi(
        #     employee=employee, salary_date=salary_sheet.date
        # )
        employee_salary.provident_fund = self.__calculate_provident_fund(
            employee=employee, salary_date=salary_sheet.date
        )

        payable_salary = employee.current_salary.payable_salary
        basic_salary = 0.55 * payable_salary

        # if basic_salary >= 25000 or employee_salary.net_salary >= 43800:
        if employee.tax_eligible:
            if not SalarySheetTaxLoan.objects.filter(
                salarysheet=salary_sheet, loan__employee=employee
            ):
                employee_tax_loan = EmployeeTaxLoanRepository(
                    employee=employee, date=self.date
                )
                monthly_tax = employee_tax_loan.calculate_tax_loan()
                if monthly_tax > 0:
                    loan_instance = Loan.objects.create(
                        employee=employee,
                        witness=Employee.objects.filter(
                            id=30
                        ).first(),  # You might need to adjust this based on your requirements
                        loan_amount=monthly_tax,  # Set the loan amount
                        emi=monthly_tax,  # Set the EMI amount
                        effective_date=timezone.now(),
                        start_date=salary_sheet.date,
                        end_date=salary_sheet.date,
                        tenor=1,  # Set the tenor/period in months
                        payment_method="salary",  # Set the payment method
                        loan_type="tds",  # Set the loan type
                    )

                    # loan_instance.save()
                    salarysheettax = SalarySheetTaxLoan.objects.create(
                        salarysheet=salary_sheet, loan=loan_instance
                    )
                    salarysheettax.save()

        employee_salary.loan_emi = self.__calculate_loan_emi(
            employee=employee, salary_date=salary_sheet.date
        )

        employee_salary.provident_fund = self.__calculate_provident_fund(
            employee=employee, salary_date=salary_sheet.date
        )
        total_fine = self.__calculate_late_entry_fine(
            employee=employee, salary_date=salary_sheet.date
        )
        salary_loans = self._calculate_salary_loan(
            employee=employee, salary_date=salary_sheet.date
        )
        employee_salary.gross_salary = (
            employee_salary.net_salary
            + employee_salary.overtime
            + employee_salary.festival_bonus
            + employee_salary.food_allowance
            + employee_salary.leave_bonus
            + employee_salary.project_bonus
            + employee_salary.code_quality_bonus
            + employee_salary.loan_emi
            + employee_salary.provident_fund
            + total_fine
            + salary_loans
            # + employee_salary.device_allowance
        )
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
            salary_sheet.date.year, salary_sheet.date.month
        )[1]
        joining_date = employee.joining_date.day
        resigned = employee.resignation_set.filter(
            status="approved", date__lte=salary_sheet.date
        ).first()
        payable_days, working_days_after_join, working_days_after_resign = 0, 0, 0
        # if employee join at salary sheet making month
        if employee.joining_date.strftime("%Y-%m") == salary_sheet.date.strftime(
            "%Y-%m"
        ):
            working_days_after_join = (working_days + 1) - joining_date
        # if employee resigned at salary sheet making month
        if resigned:
            working_days_after_resign = working_days - (resigned.date.day)
        # if employee join before salary month but resigned at the salarysheet making month
        if (
            employee.joining_date.strftime("%Y-%m")
            < salary_sheet.date.strftime("%Y-%m")
            and resigned
        ):
            working_days_after_join = working_days
        payable_days = working_days_after_join - working_days_after_resign
        # if employee join or leave or join and leave at salary sheet making month
        # print(f'Employee {employee.full_name} payable days : {payable_days}')
        latest_salary = self.__employee_current_salary
        if payable_days == 0:
            return int(latest_salary.payable_salary)
        return int((latest_salary.payable_salary / working_days) * payable_days)

    def __calculate_overtime(self, salary_sheet: SalarySheet, employee: Employee):
        """Calculate Overtime
        If employee do overtime in salary sheet making month, and count the total number of overtime

        @param salary_sheet:
        @param employee:
        @return number:
        """

        # 31 / 1.5
        return (
            self.__employee_current_salary.payable_salary / 15
        ) * employee.overtime_set.filter(
            date__month=salary_sheet.date.month,
            date__year=salary_sheet.date.year,
            status="approved",
        ).count()

    def __resignation_employee_non_paid_leave(
        self, salary_sheet: SalarySheet, employee: Employee
    ):
        """Resignation Employee Non Paid Leave
        it will calculate non paid leave if the employee left before salary sheet making month
        it should always return negative integer or zero

        @param salary_sheet:
        @param employee:
        @return negative number:
        """
        if employee.resignation_date:
            one_day_salary = self.__employee_current_salary.payable_salary / 30
            medical_non_paid_amount = 0
            casual_non_paid_amount = 0
            available_medical_leave = employee.leave_available_leaveincash(
                "medical_leave", salary_sheet.date
            )
            passed_medical_leave = employee.leave_passed(
                "medical", salary_sheet.date.year
            )
            if passed_medical_leave > available_medical_leave:
                medical_non_paid_amount = (
                    available_medical_leave - passed_medical_leave
                ) * one_day_salary

            available_casual_leave = employee.leave_available_leaveincash(
                "casual_leave", salary_sheet.date
            )
            passed_casual_leave = employee.leave_passed(
                "casual", salary_sheet.date.year
            )
            if passed_casual_leave > available_casual_leave:
                casual_non_paid_amount = (
                    available_casual_leave - passed_casual_leave
                ) * one_day_salary

            return medical_non_paid_amount + casual_non_paid_amount
        return 0

    def __calculate_non_paid_leave(self, salary_sheet: SalarySheet, employee: Employee):
        """Calculate Non Paid Leave and Half Day Non Paid Leave
        It calculates the total non-paid leave, including half-day non-paid leave where
        2 half-day leaves equal 1 full non-paid leave. It always returns a negative number.

        @param salary_sheet: The salary sheet object containing the date for the calculation
        @param employee: The employee object whose leaves are being calculated
        @return: Negative number representing the deduction for non-paid leaves
        """
        # # Filter non-paid leaves
        # non_paid_leaves = employee.leave_set.filter(
        #     start_date__month=salary_sheet.date.month,
        #     start_date__year=salary_sheet.date.year,
        #     end_date__year=salary_sheet.date.year,
        #     end_date__month=salary_sheet.date.month,
        #     leave_type="non_paid",
        #     status="approved",
        # ).aggregate(total_leave=Sum("total_leave"))["total_leave"] or 0

        # # Filter half-day non-paid leaves
        # half_day_leaves = employee.leave_set.filter(
        #     start_date__month=salary_sheet.date.month,
        #     start_date__year=salary_sheet.date.year,
        #     end_date__year=salary_sheet.date.year,
        #     end_date__month=salary_sheet.date.month,
        #     leave_type="half_day_non_paid",
        #     status="approved",
        # ).aggregate(total_leave=Sum("total_leave"))["total_leave"] or 0

        # # Convert half-day leaves to equivalent full days (2 half-days = 1 full day)
        # equivalent_full_days = non_paid_leaves + (half_day_leaves / 2)

        leaves = employee.leave_set.filter(
            Q(leave_type__in=["non_paid", "half_day_non_paid"]),
            start_date__month=salary_sheet.date.month,
            start_date__year=salary_sheet.date.year,
            end_date__year=salary_sheet.date.year,
            end_date__month=salary_sheet.date.month,
            status="approved"
        ).aggregate(
            equivalent_full_days=Sum(
                Case(
                    When(leave_type="non_paid", then=Value(1)),
                    When(leave_type="half_day_non_paid", then=Value(0.5)),
                    output_field=FloatField()
                )
            )
        )

        equivalent_full_days = leaves["equivalent_full_days"] or 0
        # print("*#"*100)
        # print(equivalent_full_days)

        if equivalent_full_days:
            total_month_day = calendar.monthrange(
                salary_sheet.date.year, salary_sheet.date.month
            )
            return (
                -(self.__employee_current_salary.payable_salary / total_month_day[1])
                * equivalent_full_days
            )
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
        total_month_day = calendar.monthrange(
            salary_sheet.date.year, salary_sheet.date.month
        )
        leave_in_cash = 0
        if (
            salary_sheet.date.month == 12
            and employee.leave_in_cash_eligibility
            and employee.permanent_date != None
        ):
            one_day_salary = (
                self.__employee_current_salary.payable_salary / total_month_day[1]
            )
            # payable_medical_leave = employee.leave_available_leaveincash(
            #     "medical_leave", salary_sheet.date
            # ) - employee.leave_passed("medical", salary_sheet.date.year)
            # payable_medical_leave_amount = (
            #     (payable_medical_leave * employee.pay_scale.leave_in_cash_medical) / 100
            # ) * one_day_salary

            payable_casual_leave = employee.leave_available_leaveincash(
                "casual_leave", salary_sheet.date
            ) - employee.leave_passed("casual", salary_sheet.date.year)
            payable_casual_leave_amount = (
                (payable_casual_leave * employee.pay_scale.leave_in_cash_casual) / 100
            ) * one_day_salary

            # leave_in_cash = payable_medical_leave_amount + payable_casual_leave_amount
            leave_in_cash = payable_casual_leave_amount

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
        Additinally if employee don't have any approved blog in current month.Then this d employee willon't receive any project bonus.

        @param salary_sheet:
        @param employee:
        @return number:
        """

        # if employee.manager or employee.lead:
        #     project_hours = employee.projecthour_set.filter(
        #         date__month=salary_sheet.date.month,
        #         date__year=salary_sheet.date.year,
        #         payable=True,
        #     ).aggregate(total_hour=Coalesce(Sum("hours"), 0.0))["total_hour"]

        #     # Hour Bonus Amount Calculation
        #     project_hours_amount = project_hours * 10

        #     return project_hours_amount
        # is_blog_approved = Blog.objects.filter(created_by__employee=employee,approved_at__month=salary_sheet.date.month,status=BlogStatus.APPROVED).exists()
        project_hours_amount = 0

        # if is_blog_approved:
        employee_project_hours = employee.employeeprojecthour_set.filter(
            project_hour__date__month=salary_sheet.date.month,
            project_hour__date__year=salary_sheet.date.year,
        ).aggregate(total_hour=Coalesce(Sum("hours"), 0.0))["total_hour"]
        project_hours_amount += employee_project_hours * 10

        if employee.manager or employee.lead:
            # Found lead hour from EmployeeProjectHour
            employee_hours_as_lead = employee.employeeprojecthour_set.filter(
                project_hour__date__month=salary_sheet.date.month,
                project_hour__date__year=salary_sheet.date.year,
                project_hour__manager=employee,
            ).aggregate(total_hour=Coalesce(Sum("hours"), 0.0))["total_hour"]

            lead_project_hours = employee.projecthour_set.filter(
                date__month=salary_sheet.date.month,
                date__year=salary_sheet.date.year,
                payable=True,
            ).aggregate(total_hour=Coalesce(Sum("hours"), 0.0))["total_hour"]

            project_hours_amount += (lead_project_hours - employee_hours_as_lead) * 10
            return project_hours_amount

        return project_hours_amount

        # return project_hours_amount

    def __calculate_code_quality_bonus(
        self, salary_sheet: SalarySheet, employee: Employee
    ):
        _, last_day = calendar.monthrange(
            salary_sheet.date.year, salary_sheet.date.month
        )
        qc_total_point = 0
        if employee.manager:
            reviews_avg = (
                CodeReview.objects.filter(
                    manager=employee,
                    created_at__month=salary_sheet.date.month,
                    created_at__year=salary_sheet.date.year,
                )
                .values("employee")
                .annotate(Sum("avg_rating"), Count("id"))
            )
            total_point = 0
            for review in reviews_avg:
                total_point += (
                    review.get("avg_rating__sum") / review.get("id__count") / 2
                )

            qc_total_point += total_point

        qc_total_point += (
            employee.codereview_set.filter(
                created_at__month=salary_sheet.date.month,
                created_at__year=salary_sheet.date.year,
            )
            .aggregate(avg=Coalesce(Avg("avg_rating"), 0.0))
            .get("avg")
        )

        # first_quarter = code_review_set.filter(created_at__day__lte=15).exists()
        # second_quarter = code_review_set.filter(created_at__day__gte=16).exists()

        # if first_quarter and second_quarter:
        qc_ratio = None
        if Config.objects.first():
            qc_ratio = Config.objects.first().qc_bonus_amount
        ratio = qc_ratio if qc_ratio else 0

        return round(qc_total_point * ratio, 2)

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
        if self.festival_bonus:
            # Determine the date for the previous and new policy cutoff
            previous_policy_cutoff = datetime(2024, 1, 1).date()
            new_policy_cutoff = self.__salary_sheet.date

            if employee.joining_date < previous_policy_cutoff:
                if employee.permanent_date:
                    # Apply previous policy
                    dtdelta = employee.joining_date + timedelta(days=180)
                    seventyFivePercent = employee.joining_date + timedelta(days=150)
                    fiftyPercent = employee.joining_date + timedelta(days=120)
                    twinteeFivePercent = employee.joining_date + timedelta(days=90)
                    tenPercent = employee.joining_date + timedelta(days=60)
                    fivePercet = employee.joining_date + timedelta(days=30)

                    basic_salary = (
                        self.__employee_current_salary.payable_salary * 55
                    ) / 100

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
                    return 0

            else:
                if employee.permanent_date:
                    joining_date = employee.joining_date
                    festival_bonus_date = self.__salary_sheet.date

                    # Calculate the difference in years using relativedelta
                    # full = employee.joining_date + timedelta(days=360)
                    # ninety_percent = employee.joining_date + timedelta(days=330)
                    # eighty_percent = employee.joining_date + timedelta(days=270)
                    # sixty_percent = employee.joining_date + timedelta(days=210)
                    # fourty_percent = employee.joining_date + timedelta(days=150)
                    # twintee_percent = employee.joining_date + timedelta(days=90)

                    delta = relativedelta(festival_bonus_date, joining_date)

                    # Calculate the total months since joining
                    months_since_joining = delta.years * 12 + delta.months
                    days_since_joining = (
                        (delta.years * 12 + delta.months) * 30
                    ) + delta.days
                    print(employee, months_since_joining)

                    basic_salary = (
                        self.__employee_current_salary.payable_salary * 55
                    ) / 100

                    if days_since_joining < 90:
                        return 0
                    elif days_since_joining >= 90 and days_since_joining < 150:
                        return round((basic_salary * 20) / 100, 2)
                    elif days_since_joining >= 150 and days_since_joining < 210:
                        return round((basic_salary * 40) / 100, 2)
                    elif days_since_joining >= 210 and days_since_joining < 270:
                        return round((basic_salary * 60) / 100, 2)
                    elif days_since_joining >= 270 and days_since_joining < 330:
                        return round((basic_salary * 80) / 100, 2)
                    elif days_since_joining >= 330 and days_since_joining < 360:
                        return round((basic_salary * 90) / 100, 2)
                    else:
                        return basic_salary

                    # if festival_bonus_date < twintee_percent:
                    #     return 0
                    # elif twintee_percent >= festival_bonus_date  and fourty_percent < festival_bonus_date:
                    #     return round((basic_salary * 20) / 100, 2)
                    # elif fourty_percent >= festival_bonus_date  and sixty_percent < festival_bonus_date:
                    #     return round((basic_salary * 40) / 100, 2)
                    # elif sixty_percent >= festival_bonus_date  and eighty_percent < festival_bonus_date:
                    #     return round((basic_salary * 60) / 100, 2)
                    # elif eighty_percent >= new_policy_cutoff  and ninety_percent < festival_bonus_date:
                    #     return round((basic_salary * 80) / 100, 2)
                    # elif ninety_percent >= festival_bonus_date:
                    #     return round((basic_salary * 90) / 100, 2)
                    # elif full >= festival_bonus_date:
                    #     return round((basic_salary * 100) / 100, 2)
                else:
                    return 0

        return 0

    def __calculate_loan_emi(self, employee: Employee, salary_date: datetime.date):
        """Calculate loan EMI if have any

        if the employee have loan and the loan does not finish it will sum all the loan emi amount
        """

        employee_loans = employee.loan_set.filter(
            start_date__lte=salary_date,
            end_date__gte=salary_date,
            loan_type="tds"
        )

        # insert into loan payment table if the sum amount is not zero
        for employee_loan in employee_loans:
            note = f"This payment has been made automated when salary sheet generated at {salary_date}"
            employee_loan.loanpayment_set.get_or_create(
                loan=employee_loan,
                payment_amount=employee_loan.emi,
                note=note,
                payment_date=salary_date,
                defaults={"payment_date": salary_date, "loan": employee_loan},
            )
        emi_amount = employee_loans.aggregate(Sum("emi"))

        return -emi_amount["emi__sum"] if emi_amount["emi__sum"] else 0.0

    def _calculate_salary_loan(self, employee: Employee, salary_date: datetime.date):
        print("month", salary_date.month)
        salary_month_start = datetime(salary_date.year, salary_date.month, 1).date()
        salary_month_end = datetime(
            salary_date.year,
            salary_date.month,
            calendar.monthrange(salary_date.year, salary_date.month)[1],
        ).date()

        employee_loans = employee.loan_set.filter(
            start_date__lte=salary_month_end,
            end_date__gte=salary_month_start,
            loan_type="salary",
        ).aggregate(Sum("emi"))
        print(employee_loans["emi__sum"], employee)

        return -employee_loans["emi__sum"] if employee_loans["emi__sum"] else 0

    def __calculate_provident_fund(
        self, employee: Employee, salary_date: datetime.date
    ):
        """Calculate provident fund amount if have any"""
        return 0.0
        if not employee.pf_eligibility:
            return 0.0

        pf_account = employee.pf_account
        monthly_amount = 0
        note = f"This payment has been made automated when salary sheet generated at {salary_date}"
        basic_salary = (
            employee.pay_scale.basic * self.__employee_current_salary.payable_salary
        ) / 100
        monthly_amount = (basic_salary * pf_account.scale) / 100

        monthly_entry = employee.pf_account.monthlyentry_set.create(
            tranx_date=salary_date,
            amount=monthly_amount,
            basic_salary=basic_salary,
            note=note,
        )

        return -monthly_amount if monthly_amount else 0.0

    # def __calculate_late_entry_fine(
    #     self, employee: Employee, salary_date: datetime.date
    # ):
    #     current_month = (
    #         datetime(salary_date).month
    #         if isinstance(salary_date, str)
    #         else salary_date.month
    #     )
    #     current_year = (
    #         datetime(salary_date).year
    #         if isinstance(salary_date, str)
    #         else salary_date.year
    #     )
    #     total_fine = LateAttendanceFine.objects.filter(
    #         employee=employee,
    #         month=current_month,
    #         year=current_year,
    #     ).aggregate(fine=Sum("total_late_attendance_fine"))
    #     return -float(total_fine.get("fine", 0)) if total_fine.get("fine") else 0.00

# my one
    # def __calculate_late_entry_fine(
    #     self, employee: Employee, salary_date: datetime.date
    # ):
    #     current_month = (
    #         datetime(salary_date).month
    #         if isinstance(salary_date, str)
    #         else salary_date.month
    #     )
    #     current_year = (
    #         datetime(salary_date).year
    #         if isinstance(salary_date, str)
    #         else salary_date.year
    #     )
    #     late_count = LateAttendanceFine.objects.filter(
    #         employee=employee,
    #         month=current_month,
    #         year=current_year,
    #     ).count()
    #     total_fine = 0.00
    #     if late_count > 3:
    #         # Apply 80 BDT for 4th to 6th late entries
    #         late_entries_4_to_6 = min(late_count, 6) - 3
    #         if late_entries_4_to_6 > 0:
    #             total_fine += late_entries_4_to_6 * 80.00
    #         # Apply 500 BDT for 7th and subsequent late entries
    #         if late_count > 6:
    #             late_entries_7_and_above = late_count - 6
    #             total_fine += late_entries_7_and_above * 500.00
        
    #     return -float(total_fine) if total_fine > 0 else 0.00
    def __calculate_late_entry_fine(self, employee: Employee, salary_date: datetime.date):
        current_month = (
            datetime(salary_date).month
            if isinstance(salary_date, str)
            else salary_date.month
        )
        print("Current Month:", current_month)
        current_year = (
            datetime(salary_date).year
            if isinstance(salary_date, str)
            else salary_date.year
        )
        print("Current Year:", current_year)
        late_count = LateAttendanceFine.objects.filter(
            employee=employee,
            month=current_month,
            year=current_year,
        ).count()
        print("Late Count:", late_count)
        total_fine = 0.00
        if late_count > 3:
            # Apply 80 BDT for 4th to 6th late entries
            late_entries_4_to_6 = min(late_count, 6) - 3
            print("Late Entries 4 to 6:", late_entries_4_to_6)
            if late_entries_4_to_6 > 0:
                total_fine += late_entries_4_to_6 * 80.00
            # Apply 500 BDT for 7th and subsequent late entries
            if late_count > 6:
                late_entries_7_and_above = late_count - 6
                print("Late Entries 7 and Above:", late_entries_7_and_above)
                total_fine += late_entries_7_and_above * 500.00
        print("Total Fine:", total_fine)
        return -float(total_fine) if total_fine > 0 else 0.00

    def __calculate_food_allowance(self, employee: Employee, salary_date):
        if not employee.lunch_allowance:
            return 0.0

        resigned = employee.resignation_set.filter(
            status="approved", date__lte=salary_date
        ).first()

        total_non_paid_leave = employee.leave_set.filter(
            start_date__month=salary_date.month,
            start_date__year=salary_date.year,
            end_date__year=salary_date.year,
            end_date__month=salary_date.month,
            leave_type="non_paid",
            status="approved",
        ).aggregate(total_leave=Sum("total_leave"))["total_leave"]

        if (
            employee.joining_date.year == salary_date.year
            and employee.joining_date.month == salary_date.month
        ):
            # Calculate the last day of the month
            last_day_of_month = timezone.datetime(
                salary_date.year, salary_date.month, 1
            ) + timedelta(days=32)
            last_day_of_month = last_day_of_month.replace(day=1) - timedelta(days=1)

            # Convert employee joining_date to datetime for compatibility
            joining_datetime = timezone.datetime(
                employee.joining_date.year,
                employee.joining_date.month,
                employee.joining_date.day,
            )

            # Calculate the number of days from the joining date to the last day of the month
            days_count = (last_day_of_month - joining_datetime).days + 1
            if total_non_paid_leave:
                days_count += total_non_paid_leave
            total_pay = days_count * 100
            return min(total_pay, 3000)
        elif resigned:
            # Calculate the first day of the salary month
            first_day_of_month = timezone.datetime(
                salary_date.year, salary_date.month, 1
            )
            days_count = (resigned.date - first_day_of_month.date()).days + 1
            if total_non_paid_leave:
                days_count -= total_non_paid_leave
            total_pay = days_count * 100
            return min(total_pay, 3000)
        else:
            if not total_non_paid_leave:
                return 3000
            if total_non_paid_leave > 30:
                return 0.00
            else:
                return 3000 - (total_non_paid_leave * 100)

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

        # skipp_days = Config.objects.first().skip_lunch_amount
        # payable_days = EmployeeAttendance.objects.filter(
        #     employee=employee,
        #     date__year=salary_date.year,
        #     date__month=salary_date.month,
        # ).aggregate(total=Coalesce(Count("id"), 0))["total"]
        # total_allowance = (payable_days - skipp_days) * 140
        # return max(total_allowance, 0)

        # fa = EmployeeFoodAllowance.objects.filter(
        #     employee_id=employee.id,
        #     date=salary_date,
        # ).last()
        # if fa:
        #     return fa.amount * 140

        return 0.0

    def __calculate_device_allowance(
        self, employee: Employee, salary_date: datetime.date
    ):
        return 2500.0 if employee.device_allowance else 0.0
