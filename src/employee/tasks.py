import calendar
import datetime
import math
from dateutil.relativedelta import relativedelta, FR

from django.core import management
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import Context, loader
from django.template.loader import get_template
from django.utils import timezone
from django.conf import settings
from django.db.models import Prefetch, Q

from employee.models import Employee, Leave, EmployeeOnline, EmployeeAttendance, PrayerInfo, EmployeeFeedback
from project_management.models import ProjectHour, EmployeeProjectHour, DailyProjectUpdate, Project


def set_default_exit_time():
    NOW = datetime.datetime.now()
    DEFAULT_EXIT_HOUR = 12 + 9 # 24 hour time == 9pm
    DEFAULT_EXIT_TIME = NOW.replace(hour=DEFAULT_EXIT_HOUR, minute=0, second=0)

    employee_onlines = EmployeeOnline.objects.filter(active=True)

    for emp_online in employee_onlines:
        attandance = emp_online.employee.employeeattendance_set.last()

        activities = attandance.employeeactivity_set.all()
        if activities.exists():
            activities = list(activities)
            start_time = activities[-1].start_time
            end_time = activities[-1].end_time
            if not end_time:
                if start_time.hour < DEFAULT_EXIT_HOUR:
                    activities[-1].end_time = DEFAULT_EXIT_TIME
                else:
                    activities[-1].end_time = start_time
                activities[-1].is_updated_by_bot = True
                activities[-1].save()


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


def no_daily_update():
    
    project_id = 92 # No Client Project - 92  # local No client Project id 2
    manager_employee_id = 30 # Shahinur Rahman - 30   # local manager id himel vai 9

    today = timezone.now().date()
    daily_update_emp_ids = DailyProjectUpdate.objects.filter(created_at__date=today).values_list('employee_id', flat=True)

    if not daily_update_emp_ids.exists():
        return 

    missing_daily_upd_emp = Employee.objects.filter(active=True).\
        exclude(manager=True).\
        exclude(id__in=daily_update_emp_ids).\
        exclude(project_eligibility=False)

    if missing_daily_upd_emp.exists():
        emps = list()
        for employee in missing_daily_upd_emp:
            emps.append(DailyProjectUpdate(
                employee_id=employee.id,
                manager_id=manager_employee_id,
                project_id=project_id,
                update='-',
            ))
        DailyProjectUpdate.objects.bulk_create(emps)

        # print("[Bot] Daily Update Done")
        

def no_project_update():
    today_date = timezone.now().date()
    from_daily_update = DailyProjectUpdate.objects.filter(project__active = True, created_at__date=today_date).values_list('project__id', flat=True).distinct()
    project_update_not_found = Project.objects.filter(active=True).exclude(id__in=from_daily_update).distinct()
    
    if not project_update_not_found.exists():
        return 

    emp = Employee.objects.filter(id=30).first()  # Shahinur Rahman - 30   # local manager id himel vai 9
    man = Employee.objects.filter(id=30).first()  # Shahinur Rahman - 30   # local manager id himel vai 9

    if project_update_not_found.exists():
        punf = list()
        for no_upd_project in project_update_not_found:
            punf.append(DailyProjectUpdate(
                employee=emp,
                manager=man,
                project_id=no_upd_project.id,
                update='-',
            ))
        DailyProjectUpdate.objects.bulk_create(punf)
        # print("[Bot] No project update")



def all_employee_offline():
    set_default_exit_time()
    no_daily_update()
    no_project_update()
    EmployeeOnline.objects.filter(active=True).update(active=False)


def bonus__project_hour__monthly(date, project_id, manager_employee_id):
    bonushour_for_feedback = 1

    employees = Employee.objects.filter(
        active=True,
        project_eligibility=True,
    ).prefetch_related(
        Prefetch(
            "employeefeedback_set",
            queryset=EmployeeFeedback.objects.filter(
                created_at__year=date.year,
                created_at__month=date.month,
            ),
        ),
    )

    project_hour = ProjectHour.objects.create(
            manager_id = manager_employee_id,
            hour_type = 'bonus',
            project_id = project_id,
            date = date,
            hours = 0,
            description = 'Bonus for Monthly Feedback',
            # forcast = 'same',
            payable = True,
        )
    
    eph = []
    total_hour = 0

    for emp in employees:
        e_hour = 0

        if len(emp.employeefeedback_set.all()) > 0:
            e_hour += bonushour_for_feedback

        if e_hour > 0:
            total_hour += e_hour
            eph.append(EmployeeProjectHour(
                project_hour = project_hour,
                hours = e_hour,
                employee=emp,
            ))
    
    project_hour.hours = total_hour
    project_hour.save()

    EmployeeProjectHour.objects.bulk_create(eph)
    print("[Bot] Monthly Bonus Done")



def bonus__project_hour_add(target_date=None):
    if not target_date:
        target_date = timezone.now().date()
    else:
        target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d').date()
    
    project_id = 20 # HR - 20 # Local HR - 4
    manager_employee_id = 30 # Shahinur Rahman - 30 # Local ID - 1
    
    bonushour_for_timelyentry = 1
    bonushour_for_hroff = 1
    bonushour_for_overtime = 1
    bonushour_for_prayer = 1
    
    # Monthly bonus if it's the last day of the month
    _, last_day = calendar.monthrange(target_date.year, target_date.month)
    if target_date.day == last_day: bonus__project_hour__monthly(target_date, project_id, manager_employee_id)
    
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
            # forcast = 'same',
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
                if al > 0 and activities[0].start_time.time() < datetime.time(hour=13, minute=0, second=1):
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

                    if inside_time >= 480: # 8 hours = 480 minute
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

