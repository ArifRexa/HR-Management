import os
import requests
from django.core.mail import EmailMessage
from settings.models import (
    Announcement,
    EmailAnnouncement,
    EmailAnnouncementAttatchment,
)
from datetime import timedelta
from django.utils import timezone
from django_q.tasks import async_task
from django.conf import settings


def announcement_all_employee_mail(
    employee_email: str,
    subject: str,
    html_body: str,
    attachment_paths: str,
    cc_email: str,
):
    email = EmailMessage()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [employee_email]
    email.cc = [cc_email]
    email.subject = subject
    email.body = html_body
    email.content_subtype = "html"
    for attachment_path in attachment_paths:
        if attachment_path:
            attachment_filename = os.path.basename(attachment_path)
            with open(attachment_path, "rb") as attachment:
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


def announcement_all_client_mail(
    client_email: str,
    subject: str,
    html_body: str,
    attachment_paths: str,
    cc_email: str,
):
    email = EmailMessage()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [client_email]
    email.cc = [cc_email]
    email.subject = subject
    email.body = html_body
    email.content_subtype = "html"
    for attachment in attachment_paths:
        if attachment:
            attachment_filename = os.path.basename(attachment)
            if attachment.__contains__("http"):
                # Fetch the PDF content from the URL
                print(attachment, "in the url")
                response = requests.get(attachment)
                email.attach(attachment_filename, response.content, response.headers["Content-Type"])
            else:
                relative_path = attachment.replace(settings.MEDIA_URL, '')
                full_file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                print(full_file_path, "in the path", relative_path)
                
                attachment_filename = os.path.basename(full_file_path)
                with open(full_file_path, "rb") as attachment:
                    email.attach(attachment_filename, attachment.read())

    email.send()


def send_chunk_email(chunk_emails, announcement_id, cc_email):
    print("chanked email has called")
    for client_email in chunk_emails:
        email_announcement = EmailAnnouncement.objects.get(id=announcement_id)
        subject = email_announcement.subject
        attachmentqueryset = EmailAnnouncementAttatchment.objects.filter(
            email_announcement=email_announcement
        )
        attachment_paths = [
            attachment.attachments.url for attachment in attachmentqueryset
        ]
        html_body = email_announcement.body

        async_task(
            "settings.tasks.announcement_all_client_mail",
            client_email,
            subject,
            html_body,
            attachment_paths,
            cc_email,
        )
