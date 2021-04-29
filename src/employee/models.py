from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from settings.models import Designation, PayScale, Leave


class Employee(TimeStampMixin, AuthorMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=60, help_text='Use (,) comma for separate phone numbers')
    cv = models.FileField(null=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                          help_text='*.PDF file only', blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    pay_scale = models.ForeignKey(PayScale, on_delete=models.CASCADE)
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
    manager = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'employees'
