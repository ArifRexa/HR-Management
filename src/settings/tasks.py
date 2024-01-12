from django.core.mail import EmailMessage

from settings.models import Announcement


def announcement_mail(employee_email: str, announcement: Announcement):
    email = EmailMessage()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [employee_email]
    email.subject = "Announcement!!"
    email.body = announcement.description
    email.content_subtype = "html"
    email.send()
