from django.contrib.auth.models import User
from django.db import models
from tinymce import models as tinymce_models

# Create your models here.
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin


class Designation(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class PayScale(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    basic = models.FloatField()
    travel_allowance = models.FloatField()
    house_allowance = models.FloatField()
    medical_allowance = models.FloatField()
    net_payable = models.FloatField()
    provision_period = models.IntegerField(help_text='Month')
    increment_period = models.IntegerField(help_text='increment month count')
    increment_rate = models.FloatField(help_text='In percentage')

    def __str__(self):
        return self.title


class LeaveManagement(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    casual_leave = models.IntegerField()
    medical_leave = models.IntegerField()

    def __str__(self):
        return self.title


class PublicHoliday(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True)

    def __str__(self):
        return self.title


class PublicHolidayDate(TimeStampMixin):
    public_holiday = models.ForeignKey(PublicHoliday, on_delete=models.CASCADE, related_name='public_holiday')
    date = models.DateField()


class Bank(TimeStampMixin, AuthorMixin):
    name = models.CharField(max_length=200)
    address = models.TextField(null=True, blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Letter(TimeStampMixin, AuthorMixin):
    header = tinymce_models.HTMLField()
    sticky_header = models.BooleanField(default=False)
    body = tinymce_models.HTMLField()
    footer = tinymce_models.HTMLField()
    sticky_footer = models.BooleanField(default=False)
