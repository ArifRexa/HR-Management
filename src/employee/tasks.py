from django.core.mail import EmailMultiAlternatives, EmailMessage

from employee.models import Employee, Leave


def send_mail_to_employee(employee, pdf, html_body, subject):
    email = EmailMultiAlternatives()
    email.subject = f'{subject} of {employee.full_name}'
    email.attach_alternative(html_body, 'text/html')
    email.to = [employee.email]
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.attach_file(pdf)
    email.send()


def leave_mail(leave: Leave):
    email = EmailMessage()
    email.from_email = leave.employee.email if leave.leave_type == 'pending' else '"Mediusware-HR" <hr@mediusware.com>'
    email.to = 'hr@mediusware.com' if leave.leave_type != 'pending' else leave.employee.email
    email.subject = f"Leave application {leave.leave_type}, {leave.status}"
    email.body = leave.message
    email.send()
