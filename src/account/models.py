import calendar
from datetime import date as dt
from datetime import datetime
from decimal import Decimal
from math import floor

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models, transaction

# Create your models here.
from django.db.models import Sum
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee, LateAttendanceFine
from inventory_management.models import InventoryTransaction
from project_management.models import Client, Project
from settings.models import FinancialYear


class SalarySheet(TimeStampMixin, AuthorMixin):
    date = models.DateField(blank=False)
    festival_bonus = models.BooleanField(default=False)
    total_value = models.FloatField(null=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    @property
    def total(self):
        return floor(
            self.employeesalary_set.aggregate(Sum("gross_salary"))[
                "gross_salary__sum"
            ]
        )

    class Meta:
        verbose_name = "Salary Sheet"
        verbose_name_plural = "Salary Sheets"
        permissions = (
            (
                "can_see_salary_on_salary_sheet",
                "Can able to see Salary on Salary Sheet",
            ),
        )


class EmployeeSalary(TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    net_salary = models.FloatField()
    overtime = models.FloatField(null=True)
    project_bonus = models.FloatField(null=True, default=0.0)
    code_quality_bonus = models.FloatField(null=True, default=0.0)
    leave_bonus = models.FloatField(null=True, default=0.0)
    festival_bonus = models.FloatField(null=True, default=0.0)
    food_allowance = models.FloatField(null=True, default=0.0)
    device_allowance = models.FloatField(null=True, default=0.0)
    loan_emi = models.FloatField(null=True, default=0.0)
    provident_fund = models.FloatField(null=True, default=0.0)
    gross_salary = models.FloatField()
    salary_sheet = models.ForeignKey(SalarySheet, on_delete=models.CASCADE)

    @property
    def gross_amount(self):
        return self.gross_salary - self.festival_bonus

    # @property
    # def salary_loan_total(self):
    #     print(self.salary_sheet.date.month,"Salary sheet month")

    #     loans = Loan.objects.filter(
    #         employee=self.employee,
    #         start_date__month=self.salary_sheet.date.month,
    #         end_date__month=self.salary_sheet.date.month,
    #         loan_type="salary"
    #     )
    #     print(loans)
    #     return -sum(loan.emi for loan in loans)

    @property
    def salary_loan_total(self):
        print(self.salary_sheet.date.month, "Salary sheet month")
        salary_date = self.salary_sheet.date
        salary_month_start = datetime(
            salary_date.year, salary_date.month, 1
        ).date()
        salary_month_end = datetime(
            salary_date.year,
            salary_date.month,
            calendar.monthrange(salary_date.year, salary_date.month)[1],
        ).date()

        loans = Loan.objects.filter(
            employee=self.employee,
            start_date__lte=salary_month_end,
            end_date__gte=salary_month_start,
            loan_type="salary",
        )
        print(loans)
        return -sum(loan.emi for loan in loans)

    @property
    def current_month_late_fee(self):
        # late_fee = (
        #     LateAttendanceFine.objects.filter(
        #         employee=self.employee,
        #         month=self.salary_sheet.date.month,
        #         year=self.salary_sheet.date.year,
        #     ).aggregate(total_fine=Sum("total_late_attendance_fine"))[
        #         "total_fine"
        #     ]
        #     or 0
        # )
        # return -late_fee
        late_count = LateAttendanceFine.objects.filter(
            employee=self.employee,
            month=self.salary_sheet.date.month,
            year=self.salary_sheet.date.year,
        ).count()

        total_fine = 0.00
        if late_count > 3:
            # Apply 80 BDT for 4th to 6th late entries
            late_entries_4_to_6 = min(late_count, 6) - 3
            if late_entries_4_to_6 > 0:
                total_fine += late_entries_4_to_6 * 80.00
            # Apply 500 BDT for 7th and subsequent late entries
            if late_count > 6:
                late_entries_7_and_above = late_count - 6
                total_fine += late_entries_7_and_above * 500.00
        return -total_fine

    @property
    def tax_loan_total(self):
        loans = Loan.objects.filter(
            employee=self.employee,
            start_date__lte=self.salary_sheet.date,
            end_date__gte=self.salary_sheet.date,
            loan_type="tds",
        )
        return -sum(loan.emi for loan in loans)


class FestivalBonusSheet(TimeStampMixin, AuthorMixin):
    date = models.DateField(blank=False)
    total_value = models.FloatField(null=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    @property
    def total(self):
        return floor(
            self.employeefestivalbonus_set.aggregate(Sum("amount"))[
                "amount__sum"
            ]
        )


class EmployeeFestivalBonus(TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    festival_bonus_sheet = models.ForeignKey(
        FestivalBonusSheet, on_delete=models.CASCADE
    )

    amount = models.FloatField(default=0)


class SalaryDisbursement(TimeStampMixin, AuthorMixin):
    disbursement_choice = (
        ("salary_account", "Salary Account"),
        ("personal_account", "Personal Account"),
    )
    title = models.CharField(max_length=100)
    employee = models.ManyToManyField(Employee)
    disbursement_type = models.CharField(
        choices=disbursement_choice, max_length=50
    )


class ExpenseGroup(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)
    account_code = models.IntegerField(null=True, blank=True)
    vds_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0.00,
    )
    tds_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0.00,
    )

    def __str__(self):
        return self.title


class ExpenseCategory(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Expense(TimeStampMixin, AuthorMixin):
    expanse_group = models.ForeignKey(ExpenseGroup, on_delete=models.RESTRICT)
    expense_category = models.ForeignKey(
        ExpenseCategory, on_delete=models.RESTRICT
    )
    note = models.TextField(null=True, blank=True)
    amount = models.FloatField()
    date = models.DateField(default=timezone.now)
    add_to_balance_sheet = models.BooleanField(default=False, verbose_name="Reviewer")
    is_approved = models.BooleanField(default=False, verbose_name="Is Checked")
    is_authorized = models.BooleanField(
        default=True, verbose_name="Is Authorized"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="approve_by",
        null=True,
        blank=True,
        verbose_name="Checked By",
    )
    
    def save(self, *args, **kwargs):

        total = self.expanseattachment_set.aggregate(Sum('amount'))['amount__sum'] or 0
        self.amount = total
        
        super().save(*args, **kwargs)

    class Meta:
        permissions = (
            (
                "can_approve_expense",
                "Can Approve Expense",
            ),
            ("can_view_all_expenses", "Can View All Expenses"),
            ("can_add_balance_sheet", "Can Add Balance Sheet"),
            ("can_see_note_field", "Can See note field")
        )


class ExpanseAttachment(TimeStampMixin, AuthorMixin):
    expanse = models.ForeignKey(Expense, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to="uploads/expanse/%y/%m")
    note = models.TextField(null=True, blank=True)
    amount = models.FloatField(default=0.00)
    inventory_ids = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="Inventory Transaction verification ID With Comma Separate Value",
    )
    inventory = models.ManyToManyField(
        "inventory_management.InventoryItem",
        blank=True,
    )

    # def save(self, *args, **kwargs):
    #     inventory_ids = self.inventory_ids
    #     id_list = inventory_ids.split(",")
    #     inventories = InventoryTransaction.objects.filter(
    #         verification_code__in=id_list, transaction_type="i"
    #     )
    #     self.inventory = inventories
    #     super().save(args, kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the parent expense's total amount
        expense = self.expanse
        total = expense.expanseattachment_set.aggregate(Sum('amount'))['amount__sum'] or 0
        expense.amount = total
        expense.save(update_fields=['amount'])

    def delete(self, *args, **kwargs):
        expense = self.expanse
        super().delete(*args, **kwargs)
        # Update the parent expense's total amount after deletion
        total = expense.expanseattachment_set.aggregate(Sum('amount'))['amount__sum'] or 0
        expense.amount = total
        expense.save(update_fields=['amount'])

    def __str__(self):
        return f"{self.expanse.expanse_group.title} ({self.amount})"
    
    class Meta:
        permissions = (
            (
                "can_update_expense_attachment",
                "Can Update Expense Attachment",
            ),
        )


class Income(TimeStampMixin, AuthorMixin):
    STATUS_CHOICE = (
        ("pending", "⌛ Pending"),
        ("hold", "✋ Hold"),
        ("approved", "✔ Approved"),
    )
    EMAIL_SEND_STATUS = (("yes", "Yes"), ("no", "No"))
    project = models.ForeignKey(
        Project, on_delete=models.RESTRICT, limit_choices_to={"active": True}
    )
    hours = models.FloatField()
    loss_hours = models.FloatField(default=0)
    hour_rate = models.FloatField(default=10.0)
    convert_rate = models.FloatField(default=90.0, help_text="BDT convert rate")
    payment = models.FloatField()
    date = models.DateField(default=timezone.now)
    note = models.TextField(null=True, blank=True, verbose_name="Client Note")
    description = models.TextField(
        null=True, blank=True, verbose_name="Hours Description"
    )
    pdf_url = models.URLField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default="pending"
    )
    add_to_balance_sheet = models.BooleanField(default=False)
    is_send_clients = models.BooleanField(default=False)
    is_send_invoice_email = models.CharField(
        default="no", choices=EMAIL_SEND_STATUS, max_length=5
    )

    def save(self, *args, **kwargs):
        hour_rate_decimal = Decimal(self.hour_rate)
        convert_rate_decimal = Decimal(self.convert_rate)
        hours = Decimal(self.hours)
        self.payment = hours * hour_rate_decimal * convert_rate_decimal
        super(Income, self).save(*args, **kwargs)

    class Meta:
        permissions = (
            (
                "can_view_income_status",
                "Can View Income Status",
            ),
            ("can_view_income_total", "Can View Income Total"),
        )


class ProfitShare(TimeStampMixin, AuthorMixin):
    user = UserForeignKey(
        limit_choices_to={"is_superuser": True}, on_delete=models.CASCADE
    )
    date = models.DateField()
    payment_amount = models.FloatField()
    note = models.TextField(null=True, blank=True)


class FundCategory(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Fund(TimeStampMixin, AuthorMixin):
    STATUS_CHOICE = (
        ("pending", "⌛ Pending"),
        ("approved", "✔ Approved"),
    )
    date = models.DateField(null=True, blank=True)
    amount = models.FloatField(default=0.0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT
    )
    fund_category = models.ForeignKey(
        FundCategory, on_delete=models.RESTRICT, null=True, blank=True
    )
    note = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default="pending"
    )

    class Meta:
        permissions = [
            ("view_fund_user", "Can view fund user in admin"),
            ("change_fund_user", "Can change fund user in admin"),
        ]


class Loan(TimeStampMixin, AuthorMixin):
    PAYMENT_METHOD = (("salary", "Bank/Cash/Salary"),)
    LOAN_TYPE = (
        ("salary", "Salary Against Loan"),
        ("tds", "Tax Deduction at Source"),
        ("security", "Security Loan"),
        ("collateral", "Collateral Loan"),
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.RESTRICT, limit_choices_to={"active": True}
    )
    witness = models.ForeignKey(
        Employee,
        on_delete=models.RESTRICT,
        related_name="witness",
        limit_choices_to={"active": True},
    )
    description = models.TextField(null=True, blank=True)
    loan_amount = models.FloatField(help_text="Load amount")
    emi = models.FloatField(help_text="Installment amount", verbose_name="EMI")
    effective_date = models.DateField(default=timezone.now)
    start_date = models.DateField()
    end_date = models.DateField()
    tenor = models.IntegerField(help_text="Period month")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD)
    loan_type = models.CharField(max_length=50, choices=LOAN_TYPE)
    tax_calan_no = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.employee}-{self.loan_amount}"

    class Meta:
        permissions = [
            ("can_view_tax_loans", "Can view tax loans"),
        ]


class SalaryEmiLoan(EmployeeSalary):
    class Meta:
        proxy = True
        verbose_name = "Monthly Salary EMI Loan"
        verbose_name_plural = "Monthly Salary EMI Loans"


class LoanGuarantor(TimeStampMixin, AuthorMixin):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    national_id_no = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField()


class LoanAttachment(TimeStampMixin, AuthorMixin):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    file = models.FileField()


class LoanPayment(TimeStampMixin, AuthorMixin):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    payment_date = models.DateField(default=timezone.now)
    payment_amount = models.FloatField()
    note = models.TextField(null=True, blank=True)


class Invoice(TimeStampMixin, AuthorMixin):
    serial_no = models.IntegerField()
    client = models.ForeignKey(Client, on_delete=models.RESTRICT)
    date_time = models.DateTimeField()


class InvoiceDetail(TimeStampMixin, AuthorMixin):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    description = models.TextField()
    unit_of_measure = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.FloatField()
    unit_price = models.FloatField()
    total = models.FloatField()
    rate_of_supplementary_duty = models.FloatField(null=True, blank=True)
    value_of_supplementary_duty = models.FloatField(null=True, blank=True)
    rate_of_vat = models.FloatField()
    amount_of_vat = models.FloatField()
    total_price_inc_all_duty = models.FloatField()


class ProjectCommission(TimeStampMixin, AuthorMixin):
    date = models.DateField(default=timezone.now)
    employee = models.ForeignKey(
        Employee, on_delete=models.RESTRICT, limit_choices_to={"active": True}
    )
    project = models.ForeignKey(
        Project, on_delete=models.RESTRICT, limit_choices_to={"active": True}
    )
    payment = models.FloatField()


class AccountJournal(AuthorMixin, TimeStampMixin):
    journal_types = (("monthly", "MONTHLY"), ("daily", "DAILY"))
    date = models.DateField(default=timezone.now)
    type = models.CharField(max_length=20, choices=journal_types)
    expenses = models.ManyToManyField(
        Expense,
        related_name="expenses",
    )
    pv_no = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.type

    def get_pdf_generate_url_payment(self):
        return reverse("account:payment_voucher", args=[str(self.id)])

    def get_pdf_generate_url_journal(self):
        return reverse("account:journal_voucher", args=[str(self.id)])

    def get_monthly_journal(self):
        return reverse("account:account_journal", args=[str(self.id)])

    def group_cost_url(self):
        return reverse("account:group_costs", args=[str(self.id)])

    def balance_sheet_url(self):
        return reverse("account:balance_sheet", args=[str(self.id)])

    def get_monthly_expense_url(self):
        return reverse("account:monthly_expense", args=[str(self.id)])

    def get_monthly_expense_attachment_url(self):
        return reverse(
            "account:monthly_expense_attachment", args=[str(self.id)]
        )


class DailyPaymentVoucher(AccountJournal):
    class Meta:
        proxy = True
        verbose_name = "Payment/Journal Voucher (Daily)"
        verbose_name_plural = "Payment/Journal Vouchers (Daily)"


class MonthlyJournal(AccountJournal):
    class Meta:
        proxy = True
        verbose_name = "Account Journal (Monthly)"
        verbose_name_plural = "Accounts Journals (Monthly)"
        


class SalarySheetTaxLoan(models.Model):
    salarysheet = models.ForeignKey(
        SalarySheet, null=True, blank=True, on_delete=models.CASCADE
    )
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)

    # Add any additional fields related to the relationship if needed

    def __str__(self):
        return f"{self.salarysheet} - {self.loan}"

    class Meta:
        verbose_name = "Salary Sheet Tax Loan"
        verbose_name_plural = "Salary Sheet Tax Loans"


@receiver(pre_delete, sender=SalarySheet)
@transaction.atomic
def delete_related_loans(sender, instance, **kwargs):
    related_loans = Loan.objects.filter(
        salarysheettaxloan__salarysheet=instance
    )
    related_loans.delete()
    related_salary_sheet_tax_loans = SalarySheetTaxLoan.objects.filter(
        salarysheet=instance
    )
    related_salary_sheet_tax_loans.delete()


class TaxDocumentInformation(TimeStampMixin):
    employee = models.ForeignKey(
        Employee,
        related_name="%(class)s",
        on_delete=models.CASCADE,
        limit_choices_to={"active": True},
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Investment Amount",
        default=0.00,
    )
    # approved = models.BooleanField(default=False)

    class Meta:
        abstract = True
        permissions = (
            (
                "tax_information_approved",
                "Can Approve Employee Tax Documents",
            ),
        )


class InvestmentAllowance(TaxDocumentInformation):
    def __str__(self):
        return f"{self.employee.full_name} Investment - {self.amount}"


class InvestmentAllowanceAttachment(TimeStampMixin):
    investment_allowance = models.ForeignKey(
        InvestmentAllowance, on_delete=models.CASCADE
    )
    document = models.FileField(upload_to="uploads/investment_allowance/")


class VehicleRebate(TaxDocumentInformation):
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Vehicle Rebate Amount",
        default=0.00,
    )

    def __str__(self):
        return f"{self.employee.full_name} Vehicle Tax - {self.amount}"


class VehicleRebateAttachment(TimeStampMixin):
    vehicle_rebate = models.ForeignKey(VehicleRebate, on_delete=models.CASCADE)
    document = models.FileField(upload_to="uploads/vehicle_rebate/")


from django.db import models


class SalaryReport(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)  # Call the original save method
    #     self.generate_salary_report()

    # def generate_salary_report(self):
    #     start_date = self.start_date
    #     end_date = self.end_date

    #     # Prepare Excel workbook
    #     wb = Workbook()
    #     ws = wb.active
    #     ws.title = f'Salary Report'

    #     # Add the heading row
    #     headings = [
    #         'SL No', 'Name of Employee', 'Designation', 'TIN',
    #         'Total Salary', 'Basic (55%)', 'House Allowance (20%)',
    #         'Conveyance (15%)', 'Medical Allowance (10%)', 'TDS', 'Chalan No'
    #     ]
    #     ws.append(headings)

    #     # Fetch employees who have salaries in the given date range
    #     employees = Employee.objects.filter(
    #         active=True, joining_date__lte=start_date
    #     ).exclude(salaryhistory__isnull=True)

    #     # Populate the Excel sheet with employee data
    #     for index, employee in enumerate(employees, start=1):
    #         # Fetch all salary records for the employee within the date range
    #         salaries = EmployeeSalary.objects.filter(
    #             employee=employee,
    #             salary_sheet__date__range=[start_date, end_date]
    #         )

    #         # Initialize totals for the employee
    #         total_gross_salary = 0
    #         total_basic_salary = 0
    #         total_house_allowance = 0
    #         total_conveyance = 0
    #         total_medical_allowance = 0

    #         # Calculate the totals for each salary within the date range
    #         for salary in salaries:
    #             gross_salary = salary.gross_salary
    #             total_gross_salary += gross_salary

    #             # Calculate salary breakdowns
    #             total_basic_salary += gross_salary * 0.55
    #             total_house_allowance += gross_salary * 0.20
    #             total_conveyance += gross_salary * 0.15
    #             total_medical_allowance += gross_salary * 0.10

    #         # Assuming the Employee model has 'tin' and 'designation' fields
    #         tin = "employee.tin"
    #         designation = employee.designation.title

    #         # Fetch TDS and Chalan No
    #         tds = "employee.get_tds_for_period(start_date, end_date)"  # Assumed to be a custom method
    #         chalan_no = "employee.get_chalan_no()"  # Assumed to be stored or calculated

    #         # Add the data to the worksheet
    #         row = [
    #             index,
    #             employee.full_name,
    #             designation,
    #             tin,
    #             floor(total_gross_salary),
    #             floor(total_basic_salary),
    #             floor(total_house_allowance),
    #             floor(total_conveyance),
    #             floor(total_medical_allowance),
    #             tds,
    #             chalan_no
    #         ]
    #         ws.append(row)
    #         print(row)
    #     # Save the workbook to a virtual file (in memory) for download
    #     response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/ms-excel')
    #     response['Content-Disposition'] = f'attachment; filename=SalaryReport_{start_date}_to_{end_date}.xlsx'
    #     return response


def get_current_financial_year():
    active_year = FinancialYear.objects.filter(active=True).first()
    return active_year.id if active_year else None


class TDSChallan(TimeStampMixin):
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]
    tds_year = models.ForeignKey(
        FinancialYear,
        on_delete=models.SET_NULL,
        null=True,
        default=get_current_financial_year,
        verbose_name="TDS Year",
        help_text="Select the financial year for which TDS is applicable",
    )
    tds_month = models.PositiveSmallIntegerField(
        choices=MONTH_CHOICES,
        default=0,
        verbose_name="TDS Month",
        help_text="Select the month for which TDS is applicable",
    )
    tds_type = models.CharField(
        max_length=10,
        choices=(("group", "Group"), ("individual", "Individual")),
        default="group",
        verbose_name="TDS Type",
    )
    date = models.DateField(verbose_name="Challan Date")
    challan_no = models.CharField(max_length=50)
    amount = models.PositiveIntegerField()
    employee = models.ManyToManyField(
        Employee,
        blank=True,
        # null=True,
        # on_delete=models.RESTRICT,
    )
    individual_employee = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="individual_employee_tds_challan",
    )
    tds_order = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Build the 1st day of the correct fiscal month
        if self.tds_year and self.tds_month and self.tds_order is None:
            fy_start_year = (
                self.tds_year.start_date.year
            )  # FinancialYear must expose .start_date
            # Months 7-12 belong to the same calendar year,
            # months 1-6 belong to the next calendar year
            if 7 <= self.tds_month <= 12:
                year = fy_start_year
            else:
                year = fy_start_year + 1

            self.tds_order = dt(year, self.tds_month, 1)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "TDS Challan"
        verbose_name_plural = "TDS Challans"

    def __str__(self):
        return self.challan_no


class AssistantFund(TimeStampMixin, AuthorMixin):
    STATUS_CHOICE = (
        ("pending", "⌛ Pending"),
        ("approved", "✔ Approved"),
    )
    date = models.DateField(null=True, blank=True)
    amount = models.FloatField(default=0.0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT
    )
    fund_category = models.ForeignKey(
        FundCategory, on_delete=models.RESTRICT, null=True, blank=True
    )
    note = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default="pending"
    )
    
    class Meta:
        permissions = [
            ("view_assistant_fund_user", "Can view assistant fund user in admin"),
            ("change_assistant_fund_user", "Can change assistant fund user in admin"),
            ("approve_assistant_fund_status", "Can approve assistant fund status"),
            ("add_assistant_fund_to_user", "Can add assistant fund to a user"),
        ]
