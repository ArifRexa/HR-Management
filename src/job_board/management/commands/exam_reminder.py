from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.core.management import BaseCommand
from django.template.loader import get_template
from django_q.tasks import async_task

from job_board.models.candidate import CandidateAssessment


class Command(BaseCommand):
    def handle(self, *args, **options):
        candidate_assessments = CandidateAssessment.objects.filter(
            candidate_job__job__active=True,
            can_start_after__isnull=False,
            exam_started_at__isnull=True)
        self.send_mail_to_candidate(candidate_assessments)

    def send_mail_to_candidate(self, candidate_assessments):
        connection = get_connection()
        connection.open()
        for candidate_assessment in candidate_assessments:
            subject = f'{candidate_assessment.candidate_job.candidate.full_name},' \
                      f' {candidate_assessment.candidate_job.job.title} || Mediusware Ltd.'
            from_email, to = 'no-reply@mediusware.com', candidate_assessment.candidate_job.candidate.email
            html_template = get_template('mail/exam/reminder.html')
            html_content = html_template.render({
                'candidate_assessment': candidate_assessment,
                'url': f'https://job.mediusware.com/exam/{candidate_assessment.unique_id}'
            })
            email = EmailMultiAlternatives(subject=subject, from_email=from_email, to=[to])
            email.attach_alternative(html_content, "text/html")
            email.send()

        connection.close()  # Close connection
