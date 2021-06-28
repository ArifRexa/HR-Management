from django.contrib.auth import hashers
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django import forms
from gdstorage.storage import GoogleDriveStorage
from tinymce.models import HTMLField

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin


# Create your models here.
class Assessment(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    score = models.FloatField()
    duration = models.FloatField()
    description = models.TextField()

    def __str__(self):
        return self.title


class AssessmentQuestion(AuthorMixin, TimeStampMixin):
    TYPE = (
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    score = models.FloatField()
    type = models.CharField(max_length=20, choices=TYPE)


class AssessmentAnswer(AuthorMixin, TimeStampMixin):
    title = models.TextField()
    score = models.FloatField()
    correct = models.BooleanField(default=False)
    assessment_question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)


class Job(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=155)
    slug = models.SlugField(max_length=255)
    job_context = models.TextField(max_length=500)
    job_description = models.TextField(null=True, blank=True)
    job_responsibility = models.TextField(null=True, blank=True)
    educational_requirement = models.TextField(null=True, blank=True)
    additional_requirement = models.TextField(null=True, blank=True)
    compensation = models.TextField(null=True, blank=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class JobSummery(AuthorMixin, TimeStampMixin):
    JOB_TYPE = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contractual', 'Contractual')
    )
    job = models.OneToOneField(Job, on_delete=models.CASCADE)
    application_deadline = models.DateField()
    experience = models.IntegerField(help_text='Experience in year')
    job_type = models.CharField(max_length=22, choices=JOB_TYPE)
    vacancy = models.IntegerField()

    def __str__(self):
        return f'{naturalday(self.application_deadline)} | {self.vacancy} | {self.job_type}'


# go_storage = GoogleDriveStorage()


class Candidate(TimeStampMixin):
    STATUS_CHOICE = (
        ('active', 'Active'),
        ('banned', 'Banned')
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=40, unique=True)
    phone = models.CharField(max_length=11, unique=True)
    password = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='candidate/avatar/', null=True, blank=True)
    cv = models.FileField(upload_to='hr/%Y/%m/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='active')

    def save(self, *args, **kwargs):
        self.password = hashers.make_password(self.password, salt='mediusware_hr')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class CandidateJob(TimeStampMixin):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.RESTRICT)
    mcq_exam_score = models.FloatField(default=0)
    written_exam_score = models.FloatField(default=0)
    viva_exam_score = models.FloatField(default=0)
