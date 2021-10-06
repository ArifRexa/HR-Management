import time

from django.core.management import BaseCommand
from django.db.models import Q
from django_q.tasks import async_task

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
        for candidate_assessment in candidate_assessments:
            async_task('job_board.management.commands.exam_reminder.send_mail', candidate_assessment,
                       group=f'Exam Reminder {candidate_assessment.candidate_job.candidate}')
            async_task('job_board.management.commands.exam_reminder.send_sms', candidate_assessment,
                       group=f'Exam Reminder SMS {candidate_assessment.candidate_job.candidate}')
            time.sleep(5)


def send_mail(candidate_assessment: CandidateAssessment):
    exam_mail = ExamMail(candidate_assessment)
    exam_mail.reminder_mail()


def send_sms(candidate_assessment: CandidateAssessment):
    exam_sms = ExamSMS(candidate_assessment)
    exam_sms.reminder_sms()
