from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timesince import timesince

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee

from account.models import Loan


class SalaryHistory(TimeStampMixin, AuthorMixin):
    payable_salary = models.FloatField()
    active_from = models.DateField(default=timezone.now)
    note = models.TextField(null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    @property
    def active_from_human(self):
        return timesince(self.active_from)


@receiver(post_save, sender=SalaryHistory)
def save_employee_attendance(sender, instance, created, **kwargs):
    if created:

        LOAN_AMOUNT = 500
        LOAN_DATE = instance.active_from + relativedelta(day=31) # Gets the maximum month of that  day
        
        # TODO: Try Catch for first employee or local
        Loan.objects.create(
            employee=instance.employee,
            witness_id=30, # Must change  to 30
            loan_amount=LOAN_AMOUNT,
            emi=LOAN_AMOUNT,
            effective_date=LOAN_DATE,
            start_date=LOAN_DATE,
            end_date=LOAN_DATE,
            tenor=1,
            payment_method='salary',
            loan_type='salary',
        )

