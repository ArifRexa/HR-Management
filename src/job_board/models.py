from django.db import models

# Create your models here.
from django.utils import timezone
from django.urls import reverse


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField()
    experience = models.CharField(max_length=255)
    last_date = models.DateField()
    position = models.IntegerField()
    file = models.ImageField(upload_to="images", blank=True, null=True)
    created_at = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'jobs'

    def get_single_url(self):
        return reverse('job-details', kwargs={"id": self.id})

    def get_apply_url(self):
        return reverse('job-apply', kwargs={"id": self.id})


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

class JobApply(models.Model):
    data = models.TextField(null=True)
    date = models.DateField(auto_now=False, auto_now_add=True, null=True)
    file = models.ImageField(upload_to="cv", blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    def __str__(self):
        return self.job.title

    class Meta:
        db_table = 'job_applys'