from decimal import Decimal
from math import floor

from django.db import transaction

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Sum
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee
from project_management.models import Project, Client
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class SalarySheet(TimeStampMixin, AuthorMixin):
    date = models.DateField(blank=False)
    festival_bonus = models.BooleanField(default=False)
    total_value = models.FloatField(null=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    @property
    def total(self):
        return floor(
            self.employeesalary_set.aggregate(Sum("gross_salary"))["gross_salary__sum"]
        )

    class Meta:
        verbose_name = "Salary Sheet"
        verbose_name_plural = "Salary Sheets"
        permissions = (
            ("can_see_salary_on_salary_sheet", "Can able to see Salary on Salary Sheet"),
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
    

class FestivalBonusSheet(TimeStampMixin, AuthorMixin):
    date = models.DateField(blank=False)
    total_value = models.FloatField(null=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    @property
    def total(self):
        return floor(
            self.employeefestivalbonus_set.aggregate(Sum("amount"))["amount__sum"]
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
    disbursement_type = models.CharField(choices=disbursement_choice, max_length=50)

class ExpenseGroup(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)
    account_code = models.IntegerField(null=True, blank=True)
    vds_rate = models.DecimalField(max_digits=4, decimal_places=2,validators=[MinValueValidator(0)], default=0.00)
    tds_rate = models.DecimalField(max_digits=4, decimal_places=2,validators=[MinValueValidator(0)], default=0.00)

    def __str__(self):
        return self.title


class ExpenseCategory(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Expense(TimeStampMixin, AuthorMixin):
    expanse_group = models.ForeignKey(ExpenseGroup, on_delete=models.RESTRICT)
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.RESTRICT)
    note = models.TextField(null=True, blank=True)
    amount = models.FloatField()
    date = models.DateField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="approve_by", null=True, blank=True
    )
    add_to_balance_sheet = models.BooleanField(default=True)

    class Meta:
        permissions = (
            (
                "can_approve_expense",
                "Can Approve Expense",
            ),
            (
                "can_view_all_expenses",
                "Can View All Expenses"
            )
        )


class ExpanseAttachment(TimeStampMixin, AuthorMixin):
    expanse = models.ForeignKey(Expense, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to="uploads/expanse/%y/%m")


class Income(TimeStampMixin, AuthorMixin):
    STATUS_CHOICE = (("pending", "⌛ Pending"), ("approved", "✔ Approved"))
    project = models.ForeignKey(
        Project, on_delete=models.RESTRICT, limit_choices_to={"active": True}
    )
    hours = models.FloatField()
    loss_hours = models.FloatField(default=0)
    hour_rate = models.FloatField(default=10.0)
    convert_rate = models.FloatField(default=90.0, help_text="BDT convert rate")
    payment = models.FloatField()
    date = models.DateField(default=timezone.now)
    note = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="pending")
    add_to_balance_sheet = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        hour_rate_decimal = Decimal(self.hour_rate)
        # convert_rate_decimal = Decimal(self.convert_rate)
        hours = Decimal(self.hours)
        self.payment = hours * hour_rate_decimal #* convert_rate_decimal
        super(Income, self).save(*args, **kwargs)


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
    date = models.DateField(null=True, blank=True)
    amount = models.FloatField(default=0.0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    fund_category = models.ForeignKey(
        FundCategory, on_delete=models.RESTRICT, null=True, blank=True
    )
    note = models.TextField(null=True, blank=True)


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
    loan_amount = models.FloatField(help_text="Load amount")
    emi = models.FloatField(help_text="Installment amount", verbose_name="EMI")
    effective_date = models.DateField(default=timezone.now)
    start_date = models.DateField()
    end_date = models.DateField()
    tenor = models.IntegerField(help_text="Period month")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD)
    loan_type = models.CharField(max_length=50, choices=LOAN_TYPE)

    def __str__(self):
        return f"{self.employee}-{self.loan_amount}"


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

from django.urls import reverse
class AccountJournal(AuthorMixin, TimeStampMixin):
    journal_types = (
        ('monthly', 'MONTHLY'),
        ('daily', 'DAILY')
    )
    date = models.DateField(default=timezone.now)
    type = models.CharField(max_length=20, choices=journal_types)
    expenses = models.ManyToManyField(Expense, related_name='expenses',)
    pv_no = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.type

    def get_pdf_generate_url(self):
        return reverse('account:payment_voucher', args=[str(self.id)])
    
    def get_monthly_journal(self):
        return reverse('account:account_journal', args=[str(self.id)])
    
    def group_cost_url(self):
        return reverse('account:group_costs', args=[str(self.id)])
    
    def balance_sheet_url(self):
        return reverse('account:balance_sheet', args=[str(self.id)])
    
class DailyPaymentVoucher(AccountJournal):
    
    class Meta:
        proxy = True
        verbose_name = 'Payment Voucher (Daily)'
        verbose_name_plural = 'Payment Vouchers (Daily)'

class MonthlyJournal(AccountJournal):

    class Meta:
        proxy = True
        verbose_name = 'Account Journal (Monthly)'
        verbose_name_plural = 'Accounts Journals (Monthly)'


class SalarySheetTaxLoan(models.Model):
    salarysheet = models.ForeignKey(SalarySheet, null=True, blank=True, on_delete=models.CASCADE)
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
    related_loans = Loan.objects.filter(salarysheettaxloan__salarysheet=instance)
    related_loans.delete()
    related_salary_sheet_tax_loans = SalarySheetTaxLoan.objects.filter(salarysheet=instance)
    related_salary_sheet_tax_loans.delete()
