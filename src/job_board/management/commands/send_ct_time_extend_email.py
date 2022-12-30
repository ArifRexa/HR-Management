from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand
from django.template.loader import get_template
from django_q.tasks import async_task

from job_board.models.candidate import Candidate, CandidateAssessment


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('candidate_id', type=int)
        parser.add_argument('candidate_assessment_id', type=int)

    def handle(self, *args, **options):
        candidate = Candidate.objects.get(pk=options['candidate_id'])
        candidate_assessment = CandidateAssessment.objects.get(pk=options['candidate_assessment_id'])
        async_task('job_board.management.commands.send_ct_time_extend_email.send_mail', candidate, candidate_assessment)


def send_mail(candidate: Candidate, candidate_assessment: CandidateAssessment):
    html_template = get_template('mail/coding_test_time_extend.html')
    html_content = html_template.render({
        'candidate': candidate,
        'candidate_assessment': candidate_assessment,
    })
    email = EmailMultiAlternatives(subject=f'Mediusware Job - Coding Test time extend')
    email.attach_alternative(html_content, 'text/html')
    email.to = [candidate.email]
    email.from_email = 'Mediusware Ltd. <no-reply@mediusware.com>'
    email.send()
