from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand
from django.template.loader import get_template
from django_q.tasks import async_task

from job_board.models.candidate import Candidate


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('candidate_id', type=int)

    def handle(self, *args, **options):
        candidate = Candidate.objects.get(pk=options['candidate_id'])
        async_task('job_board.management.commands.send_ct_time_extend_email.send_mail', candidate)


def send_mail(candidate: Candidate):
    html_template = get_template('mail/coding_test_time_extend.html')
    html_content = html_template.render({
        'candidate': candidate
    })
    email = EmailMultiAlternatives(subject=f'Mediusware Job - Coding Test time extend')
    email.attach_alternative(html_content, 'text/html')
    email.to = [candidate.email]
    email.from_email = 'Mediusware Ltd. <no-reply@mediusware.com>'
    email.send()
