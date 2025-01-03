import os
import random
import uuid
from datetime import timedelta

from django import forms
from django.contrib.auth import hashers
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_q.tasks import async_task
from django_userforeignkey.models.fields import UserForeignKey

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from job_board.models.assessment import AssessmentQuestion, Assessment
from job_board.models.job import Job


def candidate_email_path(instance, filename):
    return 'hr/candidate/{0}/{1}'.format(instance.email, filename)


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. please attach pdf or doc file')


class Candidate(TimeStampMixin):
    STATUS_CHOICE = (
        ('active', 'Active'),
        ('banned', 'Banned')
    )
    GENDER_CHOICE = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )
    APPLICATIONS_STATUS_CHOICES = (
        ('none', 'None'),
        ('waiting', 'Waiting List'),
        ('rejected', 'Rejected'),
        ('trial', 'Trial'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=40, unique=True)
    email_otp = models.CharField(max_length=10, null=True, blank=True)
    email_verified_at = models.DateField(null=True, blank=True)
    phone = models.CharField(unique=True, max_length=10)
    password = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='candidate/avatar/', null=True, blank=True)
    cv = models.FileField(upload_to=candidate_email_path, validators=[validate_file_extension])
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='active')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICE, null=True, blank=False)
    is_shortlisted = models.BooleanField(default=False)
    is_called = models.BooleanField(default=False)
    schedule_datetime = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    application_status = models.CharField(
        max_length=20,
        choices=APPLICATIONS_STATUS_CHOICES,
        default='none'
    )

    def __str__(self):
        return self.full_name

    def get_last_job(self):
        self.candidatejob_set.last()
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
    class Meta:
        permissions = (
            (
                "can_see_candidate_expected_salary",
                "Can See Candidate Expected Salary",
            ),
        )
        


class CandidateJob(TimeStampMixin):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.RESTRICT)
    expected_salary = models.FloatField()
    additional_message = models.TextField(null=True, blank=True)
    merit = models.BooleanField(null=True, blank=True)

    def save(self, *ages, **kwargs):
        super(CandidateJob, self).save(*ages, **kwargs)
        if self.candidate_assessment.count() == 0:
            for assessment in self.job.assessments.all():
                candidate_assessment = CandidateAssessment()
                candidate_assessment.candidate_job = self
                candidate_assessment.assessment = assessment
                candidate_assessment.save()
        # TODO : Schedule mail for assessment

    def __str__(self):
        return f'{self.candidate.full_name} | {self.job.title}'


class ResetPassword(TimeStampMixin):
    email = models.EmailField()
    otp = models.CharField(max_length=10)
    otp_expire_at = models.DateTimeField()
    otp_used_at = models.DateTimeField(null=True, blank=True)

    def clean_fields(self, exclude=None):
        super(ResetPassword, self).clean_fields(exclude=['otp', 'otp_expire_at'])
        if not Candidate.objects.filter(email__exact=self.email).first():
            raise ValidationError(
                {'email': 'Your given email is not found in candidate list, please insert a valid email address'})

    def save(self, *args, **kwargs):
        if self.otp_used_at is None:
            self.otp = random.randrange(100000, 999999, 6)
            self.otp_expire_at = timezone.now() + timedelta(minutes=15)
            async_task('job_board.tasks.send_otp', self.otp, self.email)
        super(ResetPassword, self).save(*args, **kwargs)


class CandidateAssessment(TimeStampMixin):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    candidate_job = models.ForeignKey(CandidateJob, on_delete=models.CASCADE, related_name='candidate_assessment')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    can_start_after = models.DateTimeField(null=True, blank=True)
    exam_started_at = models.DateTimeField(null=True, blank=True)
    exam_end_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)
    evaluation_url = models.CharField(null=True, blank=True, max_length=255)
    candidate_feedback = models.TextField(null=True, blank=True)
    step = models.JSONField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        permissions = [
            ("access_candidate_evaluation_url", "Can access candidate's evaluation url"),
        ]
        verbose_name = "Candidate Assessment"
        verbose_name_plural = "Candidate Assessments"

    @property
    def time_spend(self):
        if self.exam_end_at is not None:
            now = timezone.now()
            if self.exam_end_at >= now:
                return now - self.exam_started_at
            return 'time_up'
        return 'not_started'

    @property
    def status(self):
        if self.step is None:
            return '-'
        if self.step['current_step'] == len(self.step['question_ids']):
            return 'complete'
        return 'processing'

    @property
    def result(self):
        if not self.step:
            return '-'
        if self.score >= self.assessment.pass_score:
            return 'pass'
        return 'fail'


@receiver(post_save, sender=CandidateAssessment)
def candidate_assessment_pre_save(sender, instance, created, *args, **kwargs):
    if instance.assessment.open_to_start and instance.exam_started_at is None:
        async_task('job_board.tasks.send_exam_url', instance)
    elif not instance.assessment.open_to_start and instance.can_start_after and instance.exam_started_at is None:
        async_task('job_board.tasks.send_exam_url', instance)

    if instance.score and instance.evaluation_url:
        main_pass_score = instance.assessment.pass_score

        if instance.score < main_pass_score:
            if instance.candidateassessmentreview_set.all().exists():
                async_task('job_board.tasks.send_score_review_coding_test_mail', instance)


class CandidateAssessmentAnswer(TimeStampMixin):
    candidate_job = models.ForeignKey(CandidateJob, on_delete=models.CASCADE)
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    total_score = models.FloatField()
    answers = models.JSONField()
    score_achieve = models.FloatField()

    def __str__(self):
        return f'{self.answers}'


class CandidateAssessmentReview(TimeStampMixin, AuthorMixin):
    candidate_assessment = models.ForeignKey(CandidateAssessment, on_delete=models.CASCADE)
    note = models.TextField()


class JobPreferenceRequest(TimeStampMixin):
    email = models.EmailField()
    preferred_designation = models.CharField(max_length=100)
    cv = models.FileField(upload_to=candidate_email_path, validators=[validate_file_extension])

    def __str__(self):
        return self.email