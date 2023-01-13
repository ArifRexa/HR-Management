from dateutil.relativedelta import relativedelta, FR

from django.core import management
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import Context, loader
from django.template.loader import get_template
from django.utils import timezone
from django.conf import settings

from employee.models import Employee, Leave, EmployeeOnline, EmployeeAttendance
from project_management.models import ProjectHour, EmployeeProjectHour


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


# TODO : Resignation notification

def permanent_notification(employees):
    html_body = loader.render_to_string('mails/permanent_notification.html',
                                        context={'employees': employees, 'total_emp': len(employees)})
    email = EmailMultiAlternatives()
    email.subject = f"Permanent Notification there are {len(employees)} employee in the list of permanent"
    email.attach_alternative(html_body, 'text/html')
    email.to = ['hr@mediusware.com']
    email.bcc = ['kmrifat@gmail.com', 'coredeveloper.2013@gmail.com']
    email.from_email = 'no-reply@mediusware.com'
    email.send()


def increment_notification(employees):
    html_body = loader.render_to_string('mails/increment_notification.html',
                                        context={'employees': employees, 'total_emp': len(employees)})
    email = EmailMultiAlternatives()
    email.subject = f"Increment Notification there are {len(employees)} employee(s) in the lis of increment"
    email.attach_alternative(html_body, 'text/html')
    email.to = ['hr@mediusware.com']
    email.bcc = ['kmrifat@gmail.com', 'coredeveloper.2013@gmail.com']
    email.from_email = 'no-reply@mediusware.com'
    email.send()


def execute_increment_notification():
    management.call_command('increment_notifi')


def execute_permanent_notification():
    management.call_command('permanent_notifi')


def execute_birthday_notification():
    management.call_command('birthday_wish')


def all_employee_offline():
    employee_online = EmployeeOnline.objects.filter(active=True).all()
    for ep in employee_online:
        ep.active = False
        ep.save()

    print('[Bot] All Employee Offline ', timezone.now())


def bonus__project_hour__on_entry():
    now = timezone.now().date()

    project_id = 20 # HR - 20 # Local HR - 4
    manager_employee_id = 30 # Shahinur Rahman - 30 # Local ID - 1
    num_of_hour = 1


    current_friday = now + relativedelta(weekday=FR(0))
    if current_friday.month != now.month:
        current_friday = now + relativedelta(weekday=FR(-1))

    attendances = EmployeeAttendance.objects.filter(
        employee__active=True,
        employee__project_eligibility=True,
        date=now,
        entry_time__lt=timezone.now().time().replace(hour=13, minute=0, second=1),
    ).prefetch_related(
        "employee",
        "employeeactivity_set",
    )

    for attendance in attendances:
        if attendance.employeeactivity_set.exists():
            project_hour = ProjectHour.objects.create(
                manager_id = manager_employee_id,
                project_id = project_id,
                date = current_friday,
                hours = num_of_hour,
                description = 'Bonus for Timely Entry',
                forcast = 'same',
                payable = True,
            )
            EmployeeProjectHour.objects.create(
                    project_hour = project_hour,
                    hours = num_of_hour,
                    employee=attendance.employee,
            )
    
    print("[Bot] Entry Bonus Done! ")

