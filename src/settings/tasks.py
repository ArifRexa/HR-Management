import os
from django.core.mail import EmailMessage
from settings.models import Announcement


def announcement_mail(employee_email: str, html_body: str, attachment_path: str):
    # print(announcement.email_announcement.all())
    email = EmailMessage()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [employee_email]
    email.subject = "Announcement!!"
    email.body = html_body 
    email.content_subtype = "html"

    if attachment_path:
        attachment_filename = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as attachment:
            email.attach(attachment_filename, attachment.read())

    email.send()
