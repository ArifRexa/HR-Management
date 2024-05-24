import os
from django.core.mail import EmailMessage
from settings.models import Announcement, EmailAnnouncement, EmailAnnouncementAttatchment
from datetime import timedelta
from django.utils import timezone
from django_q.tasks import async_task


def announcement_all_employee_mail(employee_email: str, subject: str, html_body: str, attachment_paths: str):
    email = EmailMessage()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [employee_email]
    email.subject = subject
    email.body = html_body 
    email.content_subtype = "html"
    for attachment_path in attachment_paths:
        if attachment_path:
            attachment_filename = os.path.basename(attachment_path)
            with open(attachment_path, 'rb') as attachment:
                email.attach(attachment_filename, attachment.read())

    email.send()

def announcement_mail(employee_email: str, announcement: Announcement):
    email = EmailMessage()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [employee_email]
    email.subject = "Announcement!!"
    email.body = announcement.description
    email.content_subtype = "html"
    email.send()


def send_chunk_email(chunk_emails, announcement_id):
    for employee_email in chunk_emails:
        email_announcement = EmailAnnouncement.objects.get(id=announcement_id)
        subject = email_announcement.subject
        attachmentqueryset = EmailAnnouncementAttatchment.objects.filter(email_announcement=email_announcement)
        attachment_paths = [attachment.attachments.path for attachment in attachmentqueryset]
        html_body = email_announcement.body

        async_task(
                "settings.tasks.announcement_all_employee_mail", employee_email, subject, html_body, attachment_paths
            )

