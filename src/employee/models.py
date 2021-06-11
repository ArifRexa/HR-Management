import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from settings.models import Designation, PayScale, LeaveManagement


class Employee(TimeStampMixin, AuthorMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=60, help_text='Use (,) comma for separate phone numbers')
    joining_date = models.DateField(default=timezone.now())
    cv = models.FileField(null=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                          help_text='*.PDF file only', blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    leave_management = models.OneToOneField(LeaveManagement, on_delete=models.CASCADE)
    manager = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'employees'


class SalaryHistory(TimeStampMixin, AuthorMixin):
    payable_salary = models.FloatField()
    active_from = models.DateField(default=timezone.now())
    note = models.TextField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)


class Overtime(TimeStampMixin, AuthorMixin):
    date = models.DateField(null=False, help_text='Date of overtime')
    note = models.TextField(null=True, help_text='Please explain the reason for overtime')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return self.employee.full_name


class Leave(TimeStampMixin, AuthorMixin):
    # class Meta:
    #     db_table = ''

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
    message = models.TextField()
    note = models.TextField(null=True)
    leave_type = models.CharField(choices=LEAVE_CHOICE, max_length=20)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default='pending')
    status_changed_by = models.ForeignKey(User, limit_choices_to={'is_superuser': True}, null=True,
                                          on_delete=models.RESTRICT)
    status_changed_at = models.DateField(null=True)

    def clean_fields(self, exclude=('total_leave',)):
        super().clean_fields(exclude=exclude)
        if self.start_date is not None and self.end_date is not None:
            if datetime.date.today() >= self.start_date:
                raise ValidationError({'start_date': 'Start date must be greater then today'})

            if self.start_date > self.end_date:
                raise ValidationError({'end_date': "End date must be greater then or equal {}".format(self.start_date)})


class LeaveAttachment(TimeStampMixin, AuthorMixin):
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
    attachment = models.FileField(help_text='Image , PDF or Docx file ')
