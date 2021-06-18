from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from employee.model_mixin.LeaveMixin import LeaveMixin
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
    leave_management = models.ForeignKey(LeaveManagement, on_delete=models.CASCADE)
    manager = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs, ):
        if not self.active:
            self.user.is_active = False
            self.user.save()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'employees'


class SalaryHistory(TimeStampMixin, AuthorMixin):
    payable_salary = models.FloatField()
    active_from = models.DateField(default=timezone.now())
    note = models.TextField(null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)


class Overtime(TimeStampMixin, AuthorMixin):
    date = models.DateField(null=False, help_text='Date of overtime')
    note = models.TextField(null=True, help_text='Please explain the reason for overtime')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return self.employee.full_name


class Leave(TimeStampMixin, AuthorMixin, LeaveMixin):
    message = models.TextField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    status_changed_by = models.ForeignKey(User, limit_choices_to={'is_superuser': True}, null=True,
                                          on_delete=models.RESTRICT)
    status_changed_at = models.DateField(null=True)


class LeaveAttachment(TimeStampMixin, AuthorMixin):
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
    attachment = models.FileField(help_text='Image , PDF or Docx file ')


class Resignation(TimeStampMixin, AuthorMixin):
    STATUS_CHOICE = (
        ('pending', '⏳ Pending'),
        ('approved', '✔ Approved'),
        ('rejected', '⛔ Rejected'),
    )
    message = models.TextField(max_length=50)
    date = models.DateField(default=timezone.now())
    status = models.CharField(max_length=25, default='pending', choices=STATUS_CHOICE)
    approved_at = models.DateField(null=True, editable=False)
    approved_by = models.ForeignKey(User, limit_choices_to={'is_superuser': True}, null=True, on_delete=models.RESTRICT,
                                    editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, limit_choices_to={'user__is_superuser': False})
