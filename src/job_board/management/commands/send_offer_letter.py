from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand
from django.template.loader import get_template
from django_q.tasks import async_task

import config.settings
from config.utils.pdf import PDF
from job_board.models.candidate import Candidate


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('candidate_id', type=int)

    def handle(self, *args, **options):
        candidate = Candidate.objects.get(pk=options['candidate_id'])
        pdf = generate_attachment(candidate)
        async_task('job_board.management.commands.send_offer_letter.send_mail', candidate, pdf.create())


def generate_attachment(candidate: Candidate):
    pdf = PDF()
    pdf.file_name = f'offer-letter-{candidate.id}'
    pdf.template_path = 'letters/offer_letter.html'
    pdf.context = {
        'candidate': candidate,
        'seal': f"{config.settings.STATIC_ROOT}/stationary/sign_md.png"
    }
    return pdf


def send_mail(candidate: Candidate, pdf_location):
    html_template = get_template('mail/offer_letter.html')
    html_content = html_template.render({
        'candidate': candidate
    })
    email = EmailMultiAlternatives(subject=f'Mediusware Job - '
                                           f'You are selected for the position '
                                           f'of {candidate.candidatejob_set.last().job}')
    email.attach_alternative(html_content, 'text/html')
    email.attach_file(pdf_location)
    email.to = [candidate.email]
    email.from_email = 'Mediusware Ltd. <no-reply@mediusware.com>'
    email.send()
