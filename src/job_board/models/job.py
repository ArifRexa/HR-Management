from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from tinymce.models import HTMLField

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from job_board.models.assessment import Assessment


class Job(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=155)
    slug = models.SlugField(max_length=255)
    banner_image = models.ImageField(null=True, blank=True)
    assessments = models.ManyToManyField(Assessment)
    active = models.BooleanField(default=True)
    level = models.IntegerField(default=1)

    def __str__(self):
        return self.title


class JobContext(AuthorMixin):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_contexts')
    title = models.CharField(null=True, blank=True, max_length=255)
    description = HTMLField(null=True, blank=True)


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
    REGX_CHOICE = (
        ('(.*)', 'All'),
        ('(?:git@|https://)github.com[:/](.*)', 'Git Hub'),
        ('(?:https://www.|https://)linkedin.com[:/](.*)', 'Linkedin'),
        ('(?:https://www.|https://)figma.com[:/](.*)', 'Figma'),
        ('(?:https://www.|https://)behance.net[:/](.*)', 'Behance'),
        ('(?:https://www.|https://)youtube.com[:/](.*)', 'Youtube'),
        ('(?:https://www.|https://)(?:facebook|fb).com[:/](.*)', 'Facebook'),
        ('(?:https://www.|https://)twitter.com[:/](.*)', 'Twitter'),
        ('^[0-9]*$', 'NUmber Only'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='additional_fields')
    title = models.CharField(max_length=255)
    required = models.BooleanField(default=True)
    validation_regx = models.CharField(max_length=255, default='(.*)', choices=REGX_CHOICE)
