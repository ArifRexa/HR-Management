from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.timesince import timesince

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from settings.models import Designation, LeaveManagement


class Employee(TimeStampMixin, AuthorMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=60, help_text='Use (,) comma for separate phone numbers')
    joining_date = models.DateField(default=timezone.now())
    permanent_date = models.DateField(null=True, blank=True)
    cv = models.FileField(null=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                          help_text='*.PDF file only', blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    leave_management = models.ForeignKey(LeaveManagement, on_delete=models.CASCADE)
    manager = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs, ):
        self.user.is_staff = True
        if not self.active:
            self.user.is_active = False
        self.user.save()
        super().save(*args, **kwargs)

    @property
    def joining_date_human(self):
        return timesince(self.joining_date)

    @property
    def permanent_date_human(self):
        return timesince(self.permanent_date)

    @property
    def current_salary(self):
        return self.salaryhistory_set.latest('id')

    @property
    def permanent_salary(self):
        salary = self.salaryhistory_set.filter(active_from=self.permanent_date).first()
        if salary:
            return salary
        return self.current_salary

    class Meta:
        db_table = 'employees'
