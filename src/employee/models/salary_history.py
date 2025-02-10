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

    class Meta:
        permissions = (("can_see_note_field", "Can see note field"),)
