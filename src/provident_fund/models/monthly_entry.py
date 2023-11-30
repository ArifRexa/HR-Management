from django.db import models
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin

from provident_fund.models import Account


class MonthlyEntry(TimeStampMixin, AuthorMixin):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    tranx_date = models.DateField(default=timezone.now)
    amount = models.FloatField()
    basic_salary = models.FloatField()
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Monthly Entry"
        verbose_name_plural = "Monthly Entries"

    def __str__(self):
        return self.account.__str__() + self.tranx_date.strftime("%b %d, %Y")
    
    def save(self, *args, **kwargs, ):
        return super(MonthlyEntry, self).save(*args, **kwargs)

