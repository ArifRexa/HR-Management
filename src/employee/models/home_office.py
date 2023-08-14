import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin

from settings.models import PublicHolidayDate
from employee.models.employee import Employee


class HomeOffice(TimeStampMixin, AuthorMixin):
    APPLICATION_STATUS = (
        ('pending', '⏳ Pending'),
        ('approved', '✔ Approved'),
        ('rejected', '⛔ Rejected'),
    )
    employee = models.ForeignKey(Employee, limit_choices_to={'active': True}, on_delete=models.CASCADE)
    
    start_date = models.DateField(help_text='Date of Home Office Start')
    end_date = models.DateField(help_text='Date of Home Office End')

    message = models.TextField(validators=[MinLengthValidator(120)])
    
    total_day = models.FloatField()
    note = models.TextField(null=True)
    
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    status_changed_by = models.ForeignKey(
        get_user_model(), 
        limit_choices_to={'is_superuser': True}, 
        null=True,
        on_delete=models.RESTRICT,
    )
    status_changed_at = models.DateField(null=True)
    
    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.start_date > self.end_date:
            raise ValidationError({'end_date': "End date must be greater then or equal {}".format(self.start_date)})
    
    def save(self, *args, **kwargs):
        office_holidays = PublicHolidayDate.objects.filter(
            date__gte=self.start_date,
            date__lte=self.end_date,
        ).values_list('date', flat=True)
        
        delta, weekly_holiday, public_holiday = self.end_date - self.start_date, [], []
        
        self.note = ""

        for i in range(delta.days + 1):
            date = self.start_date + datetime.timedelta(days=i)
            if date.strftime("%A") in ['Saturday', 'Sunday']:
                self.note += "The date {} is weekly holiday.\n".format(date)
                weekly_holiday.append(date)
            if date in office_holidays:
                self.note += "The date {} is public holiday.\n".format(date)
                public_holiday.append(date)
        
        self.total_day = (delta.days + 1) - (len(weekly_holiday) + len(public_holiday))
        self.note += "Applied day total {}. Effective day total {}.".format(delta.days + 1, self.total_day)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.employee.full_name
    
    class Meta:
        permissions = (
            ('can_approve_homeoffice_application', 'Can Approve Home Office Application', ),
        )


class HomeOfficeAttachment(TimeStampMixin, AuthorMixin):
    homeoffice = models.ForeignKey(HomeOffice, on_delete=models.CASCADE)
    attachment = models.FileField(help_text='Image , PDF or Docx file')

