from datetime import timedelta

from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from job_board.models.candidate import CandidateAssessment


class ExamMail:

    def __init__(self, candidate_assessment: CandidateAssessment):
        self.candidate_assessment = candidate_assessment
        self.email = EmailMultiAlternatives()
        self.email.from_email = 'Mediusware Ltd. <hr@mediusware.com>'
        self.email.subject = f'{candidate_assessment.candidate_job.candidate.full_name}, ' \
                             f'{candidate_assessment.candidate_job.job.title} || Mediusware Ltd.'
        self.email.to = [candidate_assessment.candidate_job.candidate.email]
        self.exam_url = f'https://job.mediusware.com/exam/{candidate_assessment.unique_id}'

    def reminder_mail(self):
        time_limit = (timezone.now() - timedelta(days=60)).date()
        if self.candidate_assessment.updated_at < time_limit:
            return

        html_template = get_template('mail/exam/reminder.html')
        html_content = html_template.render({
            'candidate_assessment': self.candidate_assessment,
            'url': self.exam_url
        })
        self.email.attach_alternative(html_content, "text/html")
        self.email.send()

    def send_exam_mail(self):
        html_template = get_template('mail/send_exam_url.html')
        html_content = html_template.render({
            'candidate_assessment': self.candidate_assessment,
            'url': self.exam_url
        })
        self.email.attach_alternative(html_content, "text/html")
        self.email.send()
