from django.db import models

# Create your models here.
from django.utils import timezone


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField()
    experience = models.CharField(max_length=255)
    last_date = models.DateField()
    position = models.IntegerField()
    created_at = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'jobs'


class JobForm(models.Model):
    FIELD_CHOICE = [
        ('text', 'Text'),
        ('file', 'File'),
        ('email', 'Email'),
        ('url', 'URL'),
    ]
    label = models.CharField(max_length=255)
    field_type = models.CharField(choices=FIELD_CHOICE, max_length=255)
    required = models.BooleanField(default=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    class Meta:
        db_table = 'job_forms'
