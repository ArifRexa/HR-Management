import datetime
import math
from dateutil.relativedelta import relativedelta, FR

from django.core import management
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import Context, loader
from django.template.loader import get_template
from django.utils import timezone
from django.conf import settings
from django.db.models import Prefetch

from employee.models import Employee, Leave, EmployeeOnline, EmployeeAttendance, PrayerInfo
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


def bonus__project_hour_add(target_date=None):
    if not target_date:
        target_date = timezone.now().date()
    else:
        target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d').date()
    
    # print(target_date)
    
    project_id = 20 # HR - 20 # Local HR - 4
    manager_employee_id = 30 # Shahinur Rahman - 30 # Local ID - 1
    
    bonushour_for_timelyentry = 1
    bonushour_for_hroff = 1
    bonushour_for_overtime = 1
    bonushour_for_prayer = 1

    attendances = EmployeeAttendance.objects.filter(
        employee__active=True,
        employee__project_eligibility=True,
        date=target_date,
    ).prefetch_related(
        "employeeactivity_set",
        Prefetch(
            "employee",
            queryset=Employee.objects.select_related(
                "employeeonline",
            ).prefetch_related(
                Prefetch(
                    "prayerinfo_set",
                    queryset=PrayerInfo.objects.filter(created_at__date=target_date),
                ),
            )
        ),
    )

    if len(attendances) > 0:
        project_hour = ProjectHour.objects.create(
            manager_id = manager_employee_id,
            hour_type = 'bonus',
            project_id = project_id,
            date = target_date,
            hours = 0,
            description = 'Bonus for Entry / Exit / Exceeding 8 Hour / Prayer',
            forcast = 'same',
            payable = True,
        )

        eph = []
        total_hour = 0

        for attendance in attendances:
            if attendance.employeeactivity_set.exists():
                activities = list(attendance.employeeactivity_set.all())
                al = len(activities)

                e_hour = 0
                
                # If takes entry before 01:00 PM
                if attendance.entry_time < datetime.time(hour=13, minute=0, second=1):
                    # print(attendance.employee.full_name, " - entry bonus")
                    e_hour += bonushour_for_timelyentry
                
                # Prayer Bonus
                if attendance.employee.prayerinfo_set.exists():
                    prayer_info = attendance.employee.prayerinfo_set.all()[0]
                    # print(attendance.employee.full_name, " - prayer bonus:", ((prayer_info.num_of_waqt_done // 2) * bonushour_for_prayer))
                    e_hour += ((prayer_info.num_of_waqt_done // 2) * bonushour_for_prayer)
                
                # If HR OFF for that date
                if al > 0 and activities[-1].end_time and activities[-1].end_time.time() < datetime.time(hour=23, minute=45, second=1):
                    # print(attendance.employee.full_name, " - hr off bonus")
                    e_hour += bonushour_for_hroff

                    inside_time = 0

                    for i in range(al):
                        st, et = activities[i].start_time, activities[i].end_time
                        if et:
                            inside_time += (et.timestamp() - st.timestamp())

                    inside_time = math.floor(inside_time / 60) # convert to minute

                    if inside_time > 480: # 8 hours = 480 minute
                        # print(attendance.employee.full_name, " - 8 hours bonus")
                        e_hour += bonushour_for_overtime

                total_hour += e_hour
                eph.append(EmployeeProjectHour(
                    project_hour = project_hour,
                    hours = e_hour,
                    employee=attendance.employee,
                ))
        
        project_hour.hours = total_hour
        project_hour.save()

        EmployeeProjectHour.objects.bulk_create(eph)
        print("[Bot] Bonus Done")

