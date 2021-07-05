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
    # leave = Leave.objects.get(id=leave_id)
    email = EmailMessage()
    message_body = f'{leave.message} \n {leave.note} \n Status : {leave.status}'
    if leave.status == 'pending':
        email.from_email = f'{leave.employee.full_name} <{leave.employee.email}>'
        email.to = ['"Mediusware-HR" <hr@mediusware.com>']
    else:
        email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
        email.to = [f'{leave.employee.full_name} <{leave.employee.email}>']
    email.subject = f"Leave application {leave.leave_type}, {leave.status}"
    email.body = message_body
    email.send()
