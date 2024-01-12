from django.core.mail import EmailMessage

from employee.models.employee import Employee
from settings.models import Announcement


def announcement_mail(announcement: Announcement):
    employee_list = list(
        Employee.objects.filter(active=True).values_list("email", flat=True)
    )
    email = EmailMessage()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [employee_list[0]]
    # email.cc = employee_list[1:]
    email.subject = "Announcement!!"
    email.body = announcement.description
    email.content_subtype = "html"
    email.send()
