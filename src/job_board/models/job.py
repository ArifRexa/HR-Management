from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from tinymce.models import HTMLField

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from job_board.models.assessment import Assessment


class Job(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=155)
    slug = models.SlugField(max_length=255)
    job_context = HTMLField(max_length=500)
    job_description = HTMLField(null=True, blank=True)
    job_responsibility = HTMLField(null=True, blank=True)
    educational_requirement = HTMLField(null=True, blank=True)
    additional_requirement = HTMLField(null=True, blank=True)
    compensation = HTMLField(null=True, blank=True)
    assessments = models.ManyToManyField(Assessment)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class JobSummery(AuthorMixin, TimeStampMixin):
    JOB_TYPE = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contractual', 'Contractual')
    )
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='job_summery')
    application_deadline = models.DateField()
    experience = models.CharField(max_length=255)
    job_type = models.CharField(max_length=22, choices=JOB_TYPE)
    vacancy = models.IntegerField()
    salary_range = models.CharField(max_length=255)

    def __str__(self):
        return f'{naturalday(self.application_deadline)} | {self.vacancy} | {self.job_type}'


class JobAdditionalField(TimeStampMixin, AuthorMixin):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='additional_fields')
    title = models.CharField(max_length=255)
    required = models.BooleanField(default=True)
    validation_regx = models.CharField(max_length=255, null=True, blank=True)
