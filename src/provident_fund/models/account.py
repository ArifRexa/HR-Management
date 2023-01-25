from django.db import models
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin

from employee.models import Employee


class Account(TimeStampMixin, AuthorMixin):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='pf_account')

    start_date = models.DateField(default=timezone.now)
    maturity_date = models.DateField()
    scale = models.FloatField(default=10.0, help_text="Percentage of basic salary")
    note = models.TextField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.employee.full_name
    
    def save(self, *args, **kwargs, ):
        return super(Account, self).save(*args, **kwargs)

