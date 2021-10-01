from math import floor

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
# Create your models here.
from django.db.models import Sum
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee
from project_management.models import Project


class SalarySheet(TimeStampMixin, AuthorMixin):
    date = models.DateField(blank=False)
    festival_bonus = models.BooleanField(default=False)
    total_value = models.FloatField(null=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    @property
    def total(self):
        return floor(self.employeesalary_set.aggregate(Sum('gross_salary'))['gross_salary__sum'])


class EmployeeSalary(TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    net_salary = models.FloatField()
    overtime = models.FloatField(null=True)
    project_bonus = models.FloatField(null=True, default=0.0)
    leave_bonus = models.FloatField(null=True, default=0.0)
    festival_bonus = models.FloatField(null=True, default=0.0)
    gross_salary = models.FloatField()
    salary_sheet = models.ForeignKey(SalarySheet, on_delete=models.CASCADE)


class SalaryDisbursement(TimeStampMixin, AuthorMixin):
    disbursement_choice = (
        ('salary_account', 'Salary Account'),
        ('personal_account', 'Personal Account')
    )
    title = models.CharField(max_length=100)
    employee = models.ManyToManyField(Employee)
    disbursement_type = models.CharField(choices=disbursement_choice, max_length=50)


class ExpenseGroup(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)

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


class ExpanseAttachment(TimeStampMixin, AuthorMixin):
    expanse = models.ForeignKey(Expense, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='uploads/expanse/%y/%m')


class Income(TimeStampMixin, AuthorMixin):
    STATUS_CHOICE = (
        ('pending', '⌛ Pending'),
        ('approved', '✔ Approved')
    )
    project = models.ForeignKey(Project, on_delete=models.RESTRICT, limit_choices_to={'active': True})
    hours = models.FloatField()
    hour_rate = models.FloatField(default=10.0)
    payment = models.FloatField()
    date = models.DateField(default=timezone.now)
    note = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')

    def save(self, *args, **kwargs):
        self.payment = self.hours * (self.hour_rate * 80)
        super(Income, self).save(*args, **kwargs)


class ProfitShare(TimeStampMixin, AuthorMixin):
    user = UserForeignKey(limit_choices_to={'is_superuser': True}, on_delete=models.CASCADE)
    date = models.DateField()
    payment_amount = models.FloatField()


class Fund(TimeStampMixin, AuthorMixin):
    date = models.DateField()
    amount = models.FloatField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)


class Loan(TimeStampMixin, AuthorMixin):
    PAYMENT_METHOD = (
        ('salary', 'Bank/Cash/Salary'),
    )
    LOAN_TYPE = (
        ('salary', 'Salary Against Loan'),
        ('security', 'Security Loan'),
        ('collateral', 'Collateral Loan'),
    )
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, limit_choices_to={'active': True})
    witness = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='witness',
                                limit_choices_to={'active': True})
    loan_amount = models.FloatField(help_text='Load amount')
    emi = models.FloatField(help_text='Installment amount', verbose_name='EMI')
    effective_date = models.DateField(default=timezone.now)
    start_date = models.DateField()
    end_date = models.DateField()
    tenor = models.IntegerField(help_text='Period month')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD)
    loan_type = models.CharField(max_length=50, choices=LOAN_TYPE)

    def __str__(self):
        return f'{self.employee}-{self.loan_amount}'


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
    payment_amount = models.FloatField()
    note = models.TextField(null=True, blank=True)
