import datetime
import time
from datetime import timedelta
import tempfile
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils import timezone
from django_q.models import Schedule
from django_q.tasks import async_task, schedule

from job_board.mails.exam import ExamMail
from job_board.mobile_sms.exam import ExamSMS
from job_board.models.candidate import CandidateAssessment


class Command(BaseCommand):
    def handle(self, *args, **options):
        candidate_assessments = CandidateAssessment.objects.filter(
            Q(candidate_job__job__active=True, can_start_after__isnull=False, exam_started_at__isnull=True)
            | Q(candidate_job__job__active=True, assessment__open_to_start=True, exam_started_at__isnull=True)
        )
        self.send_mail_to_candidate(candidate_assessments)

    def send_mail_to_candidate(self, candidate_assessments):
        seconds = 1
        for candidate_assessment in candidate_assessments:
            seconds = seconds + 1
            schedule('job_board.management.commands.exam_reminder.send_mail', candidate_assessment.id,
                     name=f'{timezone.now().microsecond} - {candidate_assessment.candidate_job.candidate.email}',
                     schedule_type=Schedule.ONCE, next_run=timezone.now() + timedelta(minutes=seconds))
            schedule('job_board.management.commands.exam_reminder.send_sms', candidate_assessment.id,
                     name=f'{timezone.now().microsecond} - {candidate_assessment.candidate_job.candidate.phone}',
                     schedule_type=Schedule.ONCE, next_run=timezone.now() + timedelta(minutes=seconds))
            with open(f'{tempfile.gettempdir()}/schedule.text', 'a') as f: f.write(
                f'{candidate_assessment.candidate_job.candidate} - {candidate_assessment.candidate_job} \n')


def send_mail(candidate_assessment_id: int):
    candidate_assessment = CandidateAssessment.objects.get(pk=candidate_assessment_id)
    exam_mail = ExamMail(candidate_assessment)
    exam_mail.reminder_mail()


def send_sms(candidate_assessment_id: int):
    candidate_assessment = CandidateAssessment.objects.get(pk=candidate_assessment_id)
    exam_sms = ExamSMS(candidate_assessment)
    exam_sms.reminder_sms()
