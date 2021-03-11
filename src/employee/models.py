from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone

from settings.models import Designation, PayScale, Leave


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    designation = models.OneToOneField(Designation, on_delete=models.CASCADE)
    pay_scale = models.OneToOneField(PayScale, on_delete=models.CASCADE)
    leave = models.OneToOneField(Leave, on_delete=models.CASCADE)
    created_at = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'employees'
