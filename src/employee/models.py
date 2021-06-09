from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from settings.models import Designation, PayScale, Leave


class Employee(TimeStampMixin, AuthorMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=60, help_text='Use (,) comma for separate phone numbers')
    joining_date = models.DateField(default=timezone.now())
    payable_salary = models.DecimalField(decimal_places=2, max_digits=11)
    cv = models.FileField(null=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                          help_text='*.PDF file only', blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
    manager = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'employees'


class Overtime(TimeStampMixin, AuthorMixin):
    date = models.DateField(null=False, help_text='Date of overtime')
    note = models.TextField(null=True, help_text='Please explain the reason for overtime')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return self.employee.full_name
