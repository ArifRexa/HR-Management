from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone


class Designation(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class PayScale(models.Model):
    title = models.CharField(max_length=255)
    basic = models.DecimalField(decimal_places=2, max_digits=11)
    travel_allowance = models.DecimalField(decimal_places=2, max_digits=11)
    house_allowance = models.DecimalField(decimal_places=2, max_digits=11)
    medical_allowance = models.DecimalField(decimal_places=2, max_digits=11)
    provision_period = models.IntegerField(help_text='Month')
    increment_period = models.IntegerField(help_text='increment month count')
    increment_rate = models.DecimalField(decimal_places=2, help_text='In percentage', max_digits=11)
    created_at = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Leave(models.Model):
    title = models.CharField(max_length=255)
    casual_leave = models.IntegerField()
    medical_leave = models.IntegerField()
    created_at = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
