from django.core import management
from django.core.mail import EmailMultiAlternatives
from django.db.models import Value, Count
from django.template.loader import get_template
from django.utils import timezone
from django_q.tasks import async_task
from django.core.mail import EmailMessage
import os
from job_board.admin.candidate_admin import CandidateAssessment
from job_board.mobile_sms.candidate import CandidateSMS
from job_board.mobile_sms.exam import ExamSMS
from job_board.models.assessment import Assessment
from job_board.models.candidate import Candidate
from job_board.models.candidate_email import CandidateEmail,CandidateEmailAttatchment
from django.utils.html import strip_tags
from job_board.models.candidate import Candidate
from django.template import loader


def candidates_have_to_reapply(): 
    candidates_without_jobs = Candidate.objects.filter(candidatejob__isnull=True)[:30]  
    if candidates_without_jobs.exists():  
        
        candidate_emails = [candidate.email for candidate in candidates_without_jobs]    
        subject = f"Request to apply again through the job portal"
        for email in candidate_emails: 
            async_task(
                "job_board.tasks.candidate_email_to_reapply",
                email,
                subject
               
            )
            candidate = Candidate.objects.get(email=email)
            candidate.delete()


def candidate_email_to_reapply(to_email:str, subject):
    
    email = EmailMultiAlternatives()

    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [to_email]
    email.subject = subject
    html_template = get_template('mail/re_apply_alert.html')
    html_content = html_template.render({'candidate':"Applicant"})
    email.attach_alternative(html_content,'text/html')

    email.send()


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

def send_score_review_coding_test_mail(candidate_assessment: CandidateAssessment):
    print('score send check')

    reviews = []
    for c_assesment_row in candidate_assessment.candidateassessmentreview_set.all():
        final_review = c_assesment_row.note
        reviews.append(final_review)

    c_full_name = candidate_assessment.candidate_job.candidate.full_name
    html_template = get_template('mail/score_review_email.html')
    html_content = html_template.render({
        'candidate_assessment': candidate_assessment,
        'c_full_name': c_full_name,
        'reviews': reviews
    })

    email = EmailMultiAlternatives(subject=f'{c_full_name} Score and Review.')
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


def sms_promotion(promotion_sms, candidate_assessment: CandidateAssessment):
    exam_sms = ExamSMS(candidate_assessment=candidate_assessment)
    exam_sms.promotional_sms(promotion_sms)


def employee_sms_promotion(promotion_sms, candidate: Candidate):
    candidate_sms = CandidateSMS(candidate=candidate)
    candidate_sms.promotional_sms(promotion_sms)

def send_candidate_email(candidate_email:str,email_content,attachment_paths: str):
    email = EmailMultiAlternatives()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [candidate_email]
    email.subject = email_content.subject
    email.attach_alternative(email_content.body, 'text/html')
    for attachment_path in attachment_paths:
        if attachment_path:
            attachment_filename = os.path.basename(attachment_path)
            with open(attachment_path, 'rb') as attachment:
                email.attach(attachment_filename, attachment.read())
    
    email.send()
    
    
def send_chunked_emails(chunk, candidate_email_instance_id, attachment_paths):
    candidate_email_instance = CandidateEmail.objects.get(id=candidate_email_instance_id)


    print(chunk, end = "                  ")
    for email in chunk:
        print(email)
        async_task(
            "job_board.tasks.send_candidate_email", email, candidate_email_instance, attachment_paths
        )





def send_interview_email(candidate_id, interview_datetime):
    # Fetch the candidate
    candidate = Candidate.objects.get(id=candidate_id)

    # Create the email content
    subject = f"Congratulations! You've been shortlisted for an interview"
    html_template = get_template('mail/interview_confirmation.html')
    html_content = html_template.render({
        'candidate': candidate,
        'interview_datetime': interview_datetime,
        'position': candidate.candidatejob_set.last().job
    })

    # Prepare the email
    email = EmailMultiAlternatives(subject=subject)
    email.attach_alternative(html_content, 'text/html')
    email.to = [candidate.email]
    email.from_email = 'Mediusware-HR <hr@mediusware.com>'
    # Send the email
    email.send()


def send_cancellation_email(candidate_id):
    candidate = Candidate.objects.get(id=candidate_id)

    subject = "Interview Schedule Canceled"
    html_template = get_template('mail/interview_cancellation.html')
    html_content = html_template.render({
        'candidate': candidate,
        'position': candidate.candidatejob_set.last().job
    })

    email = EmailMultiAlternatives(subject=subject)
    email.attach_alternative(html_content, 'text/html')
    email.to = [candidate.email]
    email.from_email = 'Mediusware-HR <hr@mediusware.com>'
    email.send()


# def send_bulk_application_summary_email(email_list):
#     print(email_list)
#     subject = "We are looking for you"
#     html_template = get_template('mail/reopportunity_mail.html')
#
#     # Send emails in batches to avoid timeout
#     for email in email_list:
#         print(email)
#         print("ase")
#         html_content = html_template.render({
#             'email': email,
#         })
#
#         email_message = EmailMultiAlternatives(subject=subject)
#         email_message.attach_alternative(html_content, 'text/html')
#         email_message.to = [email]
#         # email_message.from_email = 'Mediusware-HR <hr@mediusware.com>'
#         email_message.from_email = 'Mediusware-HR <checkmed2025154@gmail.com>'
#         email_message.send()

def send_bulk_application_summary_email(email_list, job_title, opening_positions):
    # print(f"Opening positions: {opening_positions}")  # Debug print
    subject = f"Exciting Career Opportunity - {job_title} at Mediusware"
    html_template = get_template('mail/reopportunity_mail.html')

    for email in email_list:
        try:
            candidate = Candidate.objects.get(email=email)
            candidate_name = candidate.full_name
        except Candidate.DoesNotExist:
            candidate_name = "Candidate"

        html_content = html_template.render({
            'candidate_name': candidate_name,
            'job_title': job_title,
            'opening_positions': opening_positions,  # This now includes both title and slug
            'email': email,
        })

        email_message = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email='Mediusware-HR <hr@mediusware.com>',
            to=[email]
        )
        email_message.attach_alternative(html_content, 'text/html')
        email_message.send()




