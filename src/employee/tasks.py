from django.core.mail import EmailMultiAlternatives
from django.template import loader


def send_mail_to_employee(employee, pdf, html_body, subject):
    email = EmailMultiAlternatives()
    email.subject = f'{subject} of {employee.full_name}'
    email.attach_alternative(html_body, 'text/html')
    email.to = [employee.email]
    email.from_email = 'hr@mediusware.com'
    email.attach_file(pdf)
    email.send()
