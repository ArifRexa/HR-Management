from django.core.mail import EmailMultiAlternatives
from django.db.models import Value
from django.template.loader import get_template
from django.utils import timezone

from job_board.admin.candidate_admin import CandidateAssessment
from job_board.models.assessment import Assessment
from job_board.models.candidate import CandidateJob


def send_otp(otp, email_address):
    html_template = get_template('mail/otp.html')
    html_content = html_template.render({'otp': otp})

    email = EmailMultiAlternatives(subject='Mediusware Job - Password Reset')
    email.attach_alternative(html_content, 'text/html')
    email.to = [email_address]
    email.from_email = 'no-reply@mediusware.com'
    email.send()


def send_exam_url(candidate_assessment: CandidateAssessment):
    print('yes i \n')
    html_template = get_template('mail/send_exam_url.html')
    html_content = html_template.render({
        'candidate_assessment': candidate_assessment,
        'url': f'https://job.mediusware.com/exam/{candidate_assessment.unique_id}'
    })

    email = EmailMultiAlternatives(subject=f'Mediusware Job - {candidate_assessment.assessment.title}')
    email.attach_alternative(html_content, 'text/html')
    email.to = ['hr@mediusware.com']
    email.from_email = candidate_assessment.candidate_job.candidate.email
    email.send()


def send_evaluation_url_to_admin(candidate_assessment: CandidateAssessment):
    html_template = get_template('mail/evaluation_url_to_admin.html')
    html_content = html_template.render({
        'candidate_assessment': candidate_assessment
    })

    email = EmailMultiAlternatives(subject=f'Mediusware Job - {candidate_assessment.candidate_job.candidate}')
    email.attach_alternative(html_content, 'text/html')
    email.to = [candidate_assessment.candidate_job.candidate.email]
    email.from_email = 'no-reply@mediusware.com'
    email.send()


def send_exam_url_if(passe_exam_id, send_exam_id):
    assessment = Assessment.objects.get(pk=passe_exam_id)
    candidate_jobs = CandidateAssessment.objects.values_list('candidate_job', flat=True).filter(
        assessment_id=passe_exam_id,
        score__gte=assessment.pass_score
    ).all()

    CandidateAssessment.objects.filter(
        candidate_job__in=list(candidate_jobs),
        assessment_id=send_exam_id,
        can_start_after__isnull=True
    ).update(can_start_after=timezone.now())


def mark_merit(assessment_id: int):
    candidate_assessments = CandidateAssessment.objects.filter(assessment_id=assessment_id,
                                                               exam_end_at__lte=timezone.now(),
                                                               candidate_job__merit=None).all()
    for candidate_assessment in candidate_assessments:
        if candidate_assessment.score >= candidate_assessment.assessment.pass_score:
            candidate_assessment.candidate_job.merit = True
            candidate_assessment.candidate_job.save()
            # TODO : Send email to candidate and admin
