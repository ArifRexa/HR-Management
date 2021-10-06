from django.core import management
from django.core.mail import EmailMultiAlternatives
from django.db.models import Value, Count
from django.template.loader import get_template
from django.utils import timezone
from django_q.tasks import async_task

from job_board.admin.candidate_admin import CandidateAssessment
from job_board.models.assessment import Assessment


def send_otp(otp, email_address):
    html_template = get_template('mail/otp.html')
    html_content = html_template.render({'otp': otp})

    email = EmailMultiAlternatives(subject='Mediusware Job - Password Reset')
    email.attach_alternative(html_content, 'text/html')
    email.to = [email_address]
    email.from_email = 'Mediusware Ltd. <no-reply@mediusware.com>'
    email.send()


def send_exam_url(candidate_assessment: CandidateAssessment):
    print('yes i \n')
    html_template = get_template('mail/send_exam_url.html')
    html_content = html_template.render({
        'candidate_assessment': candidate_assessment,
        'url': f'https://job.mediusware.com/exam/{candidate_assessment.unique_id}'
    })

    email = EmailMultiAlternatives(subject=f'{candidate_assessment.candidate_job.candidate.full_name}, '
                                           f'Mediusware Job - {candidate_assessment.assessment.title}'
                                   )
    email.attach_alternative(html_content, 'text/html')
    email.to = [candidate_assessment.candidate_job.candidate.email]
    email.from_email = 'Mediusware Ltd. <hr@mediusware.com>'
    email.send()


def send_evaluation_url_to_admin(candidate_assessment: CandidateAssessment):
    html_template = get_template('mail/evaluation_url_to_admin.html')
    html_content = html_template.render({
        'candidate_assessment': candidate_assessment
    })

    email = EmailMultiAlternatives(subject=f'{candidate_assessment.candidate_job.candidate.full_name}, '
                                           f'Mediusware Job - {candidate_assessment.candidate_job.candidate}'
                                   )
    email.attach_alternative(html_content, 'text/html')
    email.to = ['hr@mediusware.com']
    email.from_email = candidate_assessment.candidate_job.candidate.email
    email.send()


def send_exam_url_if(passed_exam_id, send_exam_id):
    return management.call_command('send_exam_url', passed_exam_id, send_exam_id)


def mark_merit(assessment_id: int):
    return management.call_command('mark_merit', assessment_id)


def exam_reminder():
    return management.call_command('exam_reminder')
