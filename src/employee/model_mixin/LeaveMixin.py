import datetime

from django.core.exceptions import ValidationError
from django.db import models

from settings.models import PublicHolidayDate


class LeaveMixin(models.Model):
    LEAVE_CHOICE = (
        ('casual', 'Casual Leave'),
        ('medical', 'Medical Leave'),
        ('non_paid', 'Non Paid Leave')
    )
    LEAVE_STATUS = (
        ('pending', '⏳ Pending'),
        ('approved', '✔ Approved'),
        ('rejected', '⛔ Rejected'),
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_leave = models.FloatField()
    note = models.TextField(null=True)
    leave_type = models.CharField(choices=LEAVE_CHOICE, max_length=20)
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default='pending')

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.start_date is not None and self.end_date is not None:
            if datetime.date.today() > self.start_date:
                raise ValidationError({'start_date': 'Start date must be greater then today'})

            if self.start_date > self.end_date:
                raise ValidationError({'end_date': "End date must be greater then or equal {}".format(self.start_date)})

    def save(self, *args, **kwargs):
        office_holidays = PublicHolidayDate.objects.filter(date__gte=self.start_date,
                                                           date__lte=self.end_date).values_list('date', flat=True)
        print(office_holidays)
        delta = self.end_date - self.start_date
        weekly_holiday, public_holiday = [], []
        self.note = ""
        for i in range(delta.days + 1):
            date = self.start_date + datetime.timedelta(days=i)
            if date.strftime("%A") in ['Saturday', 'Sunday']:
                self.note += "The date {} is weekly holiday \n".format(date)
                weekly_holiday.append(date)
            if date in office_holidays:
                self.note += "The date {} is public holiday \n".format(date)
                public_holiday.append(date)
        self.total_leave = delta.days - (len(weekly_holiday) + len(public_holiday))
        self.note += "Applied day total {}. chargeable day {}".format(delta.days, self.total_leave)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
