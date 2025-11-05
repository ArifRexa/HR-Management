import calendar
import datetime
import math
from datetime import date, datetime
from django.contrib.auth.models import User
import requests
from dateutil.relativedelta import relativedelta
from django.core import management
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.models import (
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
)
from django.template import loader
from django.utils import timezone

from account.models import Loan
from employee.models import (
    Employee,
    EmployeeAttendance,
    EmployeeFeedback,
    EmployeeOnline,
    HRPolicy,
    Leave,
    NeedHelpPosition,
    PrayerInfo,
    SalaryHistory,
)
from employee.models.employee import LateAttendanceFine
from project_management.models import (
    DailyProjectUpdate,
    EmployeeProjectHour,
    Project,
    ProjectHour,
)
from settings.models import PublicHolidayDate

from .models import EmployeeAttendance


def set_default_exit_time(default_time):
    import datetime

    NOW = datetime.datetime.now()
    DEFAULT_EXIT_HOUR = int(default_time)  # 24-hour time == 12:00 AM (midnight)
    DEFAULT_EXIT_TIME = NOW.replace(
        hour=DEFAULT_EXIT_HOUR, minute=0, second=0, microsecond=0
    )

    employee_onlines = EmployeeOnline.objects.filter(active=True)
    for emp_online in employee_onlines:
        attendance = emp_online.employee.employeeattendance_set.last()

        activities = attendance.employeeactivity_set.all()
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
    employee_onlines.update(active=False)


def send_mail_to_employee(employee, pdf, html_body, subject, letter_type):
    email = EmailMultiAlternatives()
    email.subject = f"{subject} of {employee.full_name}"
    email.attach_alternative(html_body, "text/html")
    email.to = [employee.email]
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    if pdf.__contains__("http"):
        # URL of the PDF file
        pdf_url = pdf

        # Fetch the PDF content from the URL
        response = requests.get(pdf_url)

        # email.attach_alternative(html_content, 'text/html')
        print("file name:", pdf.split("/")[-1])
        email.attach(pdf.split("/")[-1], response.content, "application/pdf")
    else:
        email.attach_file(pdf)
    if letter_type == "EAL":
        hr_policy = HRPolicy.objects.last()
        file_path = hr_policy.policy_file.url
        if file_path:
            if file_path.__contains__("http"):
                pdf_url = file_path

                # Fetch the PDF content from the URL
                response = requests.get(pdf_url)

                # email.attach_alternative(html_content, 'text/html')
                print("file name:", file_path.split("/")[-1])
                email.attach(
                    file_path.split("/")[-1], response.content, "application/pdf"
                )
            else:
                email.attach_file(file_path)
    email.send()


# def leave_mail(leave: Leave):
#     leave_manage = LeaveManagement.objects.filter(leave=leave)
#     manager_email = []
#     for leave_manage_obj in leave_manage:
#         manager_email.append(leave_manage_obj.manager.email)
#     email = EmailMessage()
#     message_body = f"{leave.message} \n {leave.note} \n Status : {leave.status}"
#     if leave.status == "pending":
#         email.from_email = f"{leave.employee.full_name} <{leave.employee.email}>"
#         email.to = ['"Mediusware-HR" <hr@mediusware.com>']
#         email.cc = manager_email
#         email.subject = f"Leave application for {leave.applied_leave_type}"
#     else:
#         email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
#         email.to = [f"{leave.employee.full_name} <{leave.employee.email}>"]
#         email.subject = f"Leave application for {leave.leave_type}"
#     email.body = message_body
#     email.send()


def leave_mail(leave: Leave):
    print("start leave mail")
    # leave_manage = LeaveManagement.objects.filter(leave=leave)
    manager_email = []
    # for leave_manage_obj in leave_manage:
    #     manager_email.append(leave_manage_obj.manager.email)
    email = EmailMultiAlternatives()
    delta = leave.end_date - leave.start_date
    applied_days = delta.days + 1
    weekly_holiday = []
    public_holiday = []


    office_holidays = PublicHolidayDate.objects.filter(
        date__gte=leave.start_date, date__lte=leave.end_date
    ).values_list("date", flat=True)


    for i in range(applied_days):
        date = leave.start_date + timezone.timedelta(days=i)
        if date.strftime("%A") in ["Saturday", "Sunday"]:
            weekly_holiday.append(date)
        if date in office_holidays:
            public_holiday.append(date)

    if leave.leave_type != "non_paid":
        chargeable_days = applied_days - len(weekly_holiday) - len(public_holiday)
    else:
        chargeable_days = applied_days

    leave_type = leave.leave_type if leave.leave_type else leave.applied_leave_type
    html_body = loader.render_to_string(
        "mails/leave_mail.html",
        context={
            "leave": leave,
            "leave_type": leave_type,
            "applied_days": applied_days,
            "chargeable_days": chargeable_days,
        },
    )
    if leave.status == "pending":
        email.from_email = f"{leave.employee.full_name} <{leave.employee.email}>"
        email.to = ['"Mediusware-HR" <hr@mediusware.com>']
        email.cc = manager_email
        email.subject = (
            f"{leave.employee.full_name}: Leave application: {leave.applied_leave_type}"
        )
    else:
        email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
        email.to = [f"{leave.employee.full_name} <{leave.employee.email}>"]
        email.subject = (
            f"{leave.employee.full_name}: Leave application: {leave.leave_type}"
        )

    email.attach_alternative(html_body, "text/html")
    email.send()
    print("end leave mail")


# TODO : Resignation notification


def permanent_notification(employees):
    html_body = loader.render_to_string(
        "mails/permanent_notification.html",
        context={"employees": employees, "total_emp": len(employees)},
    )
    email = EmailMultiAlternatives()
    email.subject = f"Permanent Notification there are {len(employees)} employee in the list of permanent"
    email.attach_alternative(html_body, "text/html")
    email.to = ["admin@mediusware.com"]
    # email.bcc = ['coredeveloper.2013@gmail.com',]
    email.from_email = "no-reply@mediusware.com"
    email.send()


def increment_notification(employees):
    html_body = loader.render_to_string(
        "mails/increment_notification.html",
        context={"employees": employees, "total_emp": len(employees)},
    )
    email = EmailMultiAlternatives()
    email.subject = f"Increment Notification there are {len(employees)} employee(s) in the lis of increment"
    email.attach_alternative(html_body, "text/html")
    email.to = ["admin@mediusware.com"]
    # email.bcc = ['coredeveloper.2013@gmail.com',]
    email.from_email = "no-reply@mediusware.com"
    email.send()


def execute_increment_notification():
    management.call_command("increment_notifi")


def execute_permanent_notification():
    management.call_command("permanent_notifi")


def execute_birthday_notification():
    management.call_command("birthday_wish")


def no_daily_update():
    project_id = 92  # No Client Project - 92  # local No client Project id 2
    manager_employee_id = 30  # Shahinur Rahman - 30   # local manager id himel vai 9

    today = timezone.now().date()

    daily_update_emp_ids = (
        DailyProjectUpdate.objects.filter(created_at__date=today)
        .values_list("employee__id", flat=True)
        .distinct()
    )
    # emp_on_leave_today = Leave.objects.filter(status="approved", start_date__lte=today, end_date__gte=today).values_list('employee__id', flat=True)

    daily_update_eligibility = (
        Employee.objects.filter(active=True)
        .exclude(manager=True, lead=True)
        .exclude(project_eligibility=False)
    )

    missing_daily_update = (
        EmployeeAttendance.objects.filter(date=today)
        .filter(employee__id__in=daily_update_eligibility)
        .exclude(employee__id__in=daily_update_emp_ids)
    )

    if not missing_daily_update.exists():
        return

    if missing_daily_update.exists():
        emps = list()
        for employee in missing_daily_update:
            emps.append(
                DailyProjectUpdate(
                    employee_id=employee.employee_id,
                    manager_id=manager_employee_id,
                    project_id=project_id,
                    update="-",
                )
            )
        DailyProjectUpdate.objects.bulk_create(emps)

        # print("[Bot] Daily Update Done")


def no_project_update():
    today_date = timezone.now().date()
    today_day = today_date.strftime("%A")
    sat_or_sun_day = today_day == "Saturday" or today_day == "Sunday"
    # print(sat_or_sun_day)
    from_daily_update = (
        DailyProjectUpdate.objects.filter(
            project__active=True, created_at__date=today_date
        )
        .values_list("project__id", flat=True)
        .distinct()
    )

    if from_daily_update.exists() and not sat_or_sun_day:
        project_update_not_found = (
            Project.objects.filter(active=True)
            .exclude(id__in=from_daily_update)
            .distinct()
        )

        if not project_update_not_found.exists():
            return

        emp = Employee.objects.filter(
            id=30
        ).first()  # Shahinur Rahman - 30   # local manager id himel vai 9
        man = Employee.objects.filter(
            id=30
        ).first()  # Shahinur Rahman - 30   # local manager id himel vai 9

        if project_update_not_found.exists():
            punf = list()
            for no_upd_project in project_update_not_found:
                punf.append(
                    DailyProjectUpdate(
                        employee=emp,
                        manager=man,
                        project_id=no_upd_project.id,
                        update="-",
                    )
                )
            DailyProjectUpdate.objects.bulk_create(punf)
            # print("[Bot] No project update")
    return


def all_employee_offline():
    set_default_exit_time()
    # no_daily_update()
    # no_project_update()
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
        manager_id=manager_employee_id,
        hour_type="bonus",
        project_id=project_id,
        date=date,
        hours=0,
        description="Bonus for Monthly Feedback",
        # forcast = 'same',
        payable=True,
    )

    eph = []
    total_hour = 0

    for emp in employees:
        e_hour = 0

        if len(emp.employeefeedback_set.all()) > 0:
            e_hour += bonushour_for_feedback

        if e_hour > 0:
            total_hour += e_hour
            eph.append(
                EmployeeProjectHour(
                    project_hour=project_hour,
                    hours=e_hour,
                    employee=emp,
                )
            )

    project_hour.hours = total_hour
    project_hour.save()

    EmployeeProjectHour.objects.bulk_create(eph)
    print("[Bot] Monthly Bonus Done")


def bonus__project_hour_add(target_date=None):
    if not target_date:
        target_date = timezone.now().date()
    else:
        target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()

    project_id = 20  # HR - 20 # Local HR - 4
    manager_employee_id = 30  # Shahinur Rahman - 30 # Local ID - 1

    bonushour_for_timelyentry = 0
    bonushour_for_hroff = 0
    bonushour_for_overtime = 0
    bonushour_for_prayer = 0

    # Monthly bonus if it's the last day of the month
    _, last_day = calendar.monthrange(target_date.year, target_date.month)
    if target_date.day == last_day:
        bonus__project_hour__monthly(target_date, project_id, manager_employee_id)

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
            ),
        ),
    )

    if len(attendances) > 0:
        # project_hour = ProjectHour.objects.create(
        #     manager_id = manager_employee_id,
        #     hour_type = 'bonus',
        #     project_id = project_id,
        #     date = target_date,
        #     hours = 0,
        #     description = 'Bonus for Entry / Exit / Exceeding 8 Hour / Prayer',
        #     # forcast = 'same',
        #     payable = True,
        # )

        eph = []
        total_hour = 0

        for attendance in attendances:
            if attendance.employeeactivity_set.exists():
                activities = list(attendance.employeeactivity_set.all())
                al = len(activities)

                e_hour = 0

                # If takes entry before 01:00 PM
                if al > 0 and activities[0].start_time.time() < datetime.time(
                    hour=13, minute=0, second=1
                ):
                    # print(attendance.employee.full_name, " - entry bonus")
                    e_hour += bonushour_for_timelyentry

                # Prayer Bonus
                if attendance.employee.prayerinfo_set.exists():
                    prayer_info = attendance.employee.prayerinfo_set.all()[0]
                    # print(attendance.employee.full_name, " - prayer bonus:", ((prayer_info.num_of_waqt_done // 2) * bonushour_for_prayer))
                    e_hour += (prayer_info.num_of_waqt_done // 2) * bonushour_for_prayer

                # If HR OFF for that date
                if (
                    al > 0
                    and activities[-1].end_time
                    and activities[-1].end_time.time()
                    < datetime.time(hour=23, minute=45, second=1)
                ):
                    # print(attendance.employee.full_name, " - hr off bonus")
                    e_hour += bonushour_for_hroff

                    inside_time = 0

                    for i in range(al):
                        st, et = activities[i].start_time, activities[i].end_time
                        if et:
                            inside_time += et.timestamp() - st.timestamp()

                    inside_time = math.floor(inside_time / 60)  # convert to minute

                    if inside_time >= 480:  # 8 hours = 480 minute
                        # print(attendance.employee.full_name, " - 8 hours bonus")
                        e_hour += bonushour_for_overtime

                total_hour += e_hour
                # eph.append(EmployeeProjectHour(
                #     project_hour = project_hour,
                #     hours = e_hour,
                #     employee=attendance.employee,
                # ))

        # project_hour.hours = total_hour
        # project_hour.save()

        # EmployeeProjectHour.objects.bulk_create(eph)
        print("[Bot] Bonus Done")


from employee.mail import cto_help_mail, hr_help_mail, send_need_help_mails
from employee.models import Config


def cto_help_pending_alert():
    current_time = timezone.now()

    # Send an email on office day every 2 hour.
    if current_time.weekday() > 4 or current_time.hour not in [12, 15, 18, 21]:
        return

    employees = Employee.objects.filter(need_cto=True)
    if Config.objects.first().cto_email is not None and employees is not None:
        email_list = Config.objects.first().cto_email.strip()
        email_list = email_list.split(",")

        for employee in employees:
            cto_help_mail(
                employee, {"waitting_at": employee.need_cto_at, "receiver": email_list}
            )


def hr_help_pending_alert():
    current_time = timezone.now()

    # Send an email on office day every 2 hour.
    if current_time.weekday() > 4 or current_time.hour not in [12, 15, 18, 21]:
        return

    employees = Employee.objects.filter(need_hr=True)
    if Config.objects.first().hr_email is not None and employees is not None:
        email_list = Config.objects.first().hr_email.strip()
        email_list = email_list.split(",")

        for employee in employees:
            hr_help_mail(
                employee, {"waiting_at": employee.need_hr_at, "receiver": email_list}
            )


def need_help_pending_alert():
    current_time = timezone.now()

    # Send an email on office day every 2 hour.
    if current_time.weekday() > 4 or current_time.hour not in [12, 14, 15, 18, 21]:
        return

    need_help_positions = NeedHelpPosition.objects.filter(active=True)
    for need_help_position in need_help_positions:
        employee_need_helps = need_help_position.employeeneedhelp_set.all()
        for employee_need_help in employee_need_helps:
            send_need_help_mails(employee_need_help)


def create_tds():
    today = timezone.now().date()
    recent_salary = (
        SalaryHistory.objects.filter(
            employee=OuterRef("pk"),
            active_from__lte=today,
        )
        .order_by("-active_from", "-id")
        .values("payable_salary")[:1]
    )

    employees = (
        Employee.objects.annotate(
            max_payable_salary=Subquery(recent_salary),
            counted_salary_amount=ExpressionWrapper(
                F("max_payable_salary") * (F("pay_scale__basic") / 100.0),
                output_field=FloatField(),
            ),
        )
        .filter(
            Q(active=True),
            Q(gender="male", counted_salary_amount__gte=25000.0)
            | Q(gender="female", counted_salary_amount__gte=28571.0),
        )
        .order_by("id")
    )

    LOAN_AMOUNT = 417
    LOAN_DATE = today + relativedelta(day=31)  # Gets the maximum month of that  day

    loans = list()
    for employee in employees:
        loans.append(
            Loan(
                employee=employee,
                witness_id=30,  # Must change  to 30
                loan_amount=LOAN_AMOUNT,
                emi=LOAN_AMOUNT,
                effective_date=LOAN_DATE,
                start_date=LOAN_DATE,
                end_date=LOAN_DATE,
                tenor=1,
                payment_method="salary",
                loan_type="tds",
            )
        )
    Loan.objects.bulk_create(loans)


# onetime call function for creating all entry_pass_id
def save_entry_pass_id():
    all_employees = Employee.objects.all()
    for employee in all_employees:
        employee.entry_pass_id = (
            f"{employee.joining_date.strftime('%Y%d')}{employee.id}"
        )
        employee.save()
    print("All Saved.")


def employee_attendance_old_data_delete(months):
    current_date = datetime.now()
    months_ago = relativedelta(months=months)

    target_date = current_date - months_ago
    old_data = EmployeeAttendance.objects.filter(created_at__lt=target_date)

    old_data.delete()


from datetime import time

# 1st one
# def late_attendance_calculate(late_entry_time=None):
#     employees = Employee.objects.filter(
#         active=True, show_in_attendance_list=True, exception_la=False  #exception_la = exception_late_attendance if true then thats are not counted as late
#     ).exclude(salaryhistory__isnull=True)
#     late_entry = late_entry_time if late_entry_time else time(hour=11, minute=11)

#     current_date = datetime.now()
#     current_month = current_date.month
#     current_year = current_date.year

#     for employee in employees:
#         total_consider = LateAttendanceFine.objects.filter(
#             employee=employee,
#             date__year=current_year,
#             date__month=current_month,
#             is_consider=True,
#         ).count()

#         # Count late entries for the current month
#         total_late_entry = (
#             EmployeeAttendance.objects.filter(
#                 employee=employee,
#                 date__year=current_year,
#                 date__month=current_month,
#                 entry_time__gt=late_entry,
#             ).count()
#             - total_consider
#         )

#         # Check if there is a late entry for today
#         today_late_entry = EmployeeAttendance.objects.filter(
#             employee=employee, date=current_date, entry_time__gt=late_entry
#         )
#         # TODO: month and year remove
#         if not LateAttendanceFine.objects.filter(
#             employee=employee,
#             # month=current_month,
#             # year=current_year,
#             date=current_date,
#         ).exists():
#             if total_late_entry > 6 and today_late_entry.exists():
#                 LateAttendanceFine.objects.create(
#                     employee=employee,
#                     month=current_month,
#                     year=current_year,
#                     date=current_date,
#                     is_consider=False,
#                     total_late_attendance_fine=500.00,
#                     entry_time=(
#                         today_late_entry.first().entry_time
#                         if today_late_entry.exists()
#                         else None
#                     ),
#                 )
#                 html_body = loader.render_to_string(
#                     "mails/late_entry_mail.html",
#                     context={
#                         "employee": employee,
#                         "entry_time": today_late_entry.first().entry_time,
#                     },
#                 )
#                 email = EmailMultiAlternatives()
#                 email.subject = f"Attention Required: Late Entry Logged {current_date}"
#                 email.attach_alternative(html_body, "text/html")
#                 email.to = [employee.email]
#                 email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
#                 email.send()

#             elif total_late_entry > 3 and today_late_entry.exists():
#                 LateAttendanceFine.objects.create(
#                     employee=employee,
#                     month=current_month,
#                     year=current_year,
#                     date=current_date,
#                     is_consider=False,
#                     total_late_attendance_fine=80.00,
#                     entry_time=(
#                         today_late_entry.first().entry_time
#                         if today_late_entry.exists()
#                         else None
#                     ),
#                 )

#                 html_body = loader.render_to_string(
#                     "mails/late_entry_mail.html",
#                     context={
#                         "employee": employee,
#                         "entry_time": today_late_entry.first().entry_time,
#                     },
#                 )
#                 email = EmailMultiAlternatives()
#                 email.subject = f"Attention Required: Late Entry Logged {current_date}"
#                 email.attach_alternative(html_body, "text/html")
#                 email.to = [employee.email]
#                 email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
#                 email.send()

#             elif total_late_entry <= 3 and today_late_entry.exists():
#                 LateAttendanceFine.objects.create(
#                     employee=employee,
#                     month=current_month,
#                     year=current_year,
#                     date=current_date,
#                     is_consider=False,
#                     total_late_attendance_fine=0.00,
#                     entry_time=(
#                         today_late_entry.first().entry_time
#                         if today_late_entry.exists()
#                         else None
#                     ),
#                 )
#     # send_absent_without_leave_email()            




# def late_attendance_calculate(late_entry_time=None):
#     employees = Employee.objects.filter(
#         active=True, show_in_attendance_list=True, exception_la=False
#     ).exclude(salaryhistory__isnull=True)
#     late_entry = late_entry_time if late_entry_time else time(hour=11, minute=11)

#     current_date = datetime.now()
#     current_month = current_date.month
#     current_year = current_date.year

#     for employee in employees:
#         total_consider = LateAttendanceFine.objects.filter(
#             employee=employee,
#             date__year=current_year,
#             date__month=current_month,
#             is_consider=True,
#         ).count()

#         # Count late entries for the current month
#         total_late_entry = (
#             EmployeeAttendance.objects.filter(
#                 employee=employee,
#                 date__year=current_year,
#                 date__month=current_month,
#                 entry_time__gt=late_entry,
#             ).count()
#             - total_consider
#         )

#         # Check if there is a late entry for today
#         today_late_entry = EmployeeAttendance.objects.filter(
#             employee=employee, date=current_date, entry_time__gt=late_entry
#         )

#         if not LateAttendanceFine.objects.filter(
#             employee=employee,
#             date=current_date,
#         ).exists():
#             if total_late_entry > 6 and today_late_entry.exists():
#                 LateAttendanceFine.objects.create(
#                     employee=employee,
#                     month=current_month,
#                     year=current_year,
#                     date=current_date,
#                     is_consider=False,
#                     total_late_attendance_fine=500.00,
#                     entry_time=(
#                         today_late_entry.first().entry_time
#                         if today_late_entry.exists()
#                         else None
#                     ),
#                 )
#                 html_body = loader.render_to_string(
#                     "mails/late_entry_mail.html",
#                     context={
#                         "employee": employee,
#                         "entry_time": today_late_entry.first().entry_time,
#                         "late_count": total_late_entry + 1,  # Include today's late entry
#                     },
#                 )
#                 email = EmailMultiAlternatives()
#                 email.subject = f"Attention Required: Late Entry Logged {current_date}"
#                 email.attach_alternative(html_body, "text/html")
#                 email.to = [employee.email]
#                 email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
#                 email.send()

#             elif total_late_entry > 3 and today_late_entry.exists():
#                 LateAttendanceFine.objects.create(
#                     employee=employee,
#                     month=current_month,
#                     year=current_year,
#                     date=current_date,
#                     is_consider=False,
#                     total_late_attendance_fine=80.00,
#                     entry_time=(
#                         today_late_entry.first().entry_time
#                         if today_late_entry.exists()
#                         else None
#                     ),
#                 )
#                 html_body = loader.render_to_string(
#                     "mails/late_entry_mail.html",
#                     context={
#                         "employee": employee,
#                         "entry_time": today_late_entry.first().entry_time,
#                         "late_count": total_late_entry + 1,  # Include today's late entry
#                     },
#                 )
#                 email = EmailMultiAlternatives()
#                 email.subject = f"Attention Required: Late Entry Logged {current_date}"
#                 email.attach_alternative(html_body, "text/html")
#                 email.to = [employee.email]
#                 email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
#                 email.send()

#             elif total_late_entry <= 3 and today_late_entry.exists():
#                 LateAttendanceFine.objects.create(
#                     employee=employee,
#                     month=current_month,
#                     year=current_year,
#                     date=current_date,
#                     is_consider=False,
#                     total_late_attendance_fine=0.00,
#                     entry_time=(
#                         today_late_entry.first().entry_time
#                         if today_late_entry.exists()
#                         else None
#                     ),
#                 )
#                 html_body = loader.render_to_string(
#                     "mails/late_entry_mail.html",
#                     context={
#                         "employee": employee,
#                         "entry_time": today_late_entry.first().entry_time,
#                         "late_count": total_late_entry + 1,  # Include today's late entry
#                     },
#                 )
#                 email = EmailMultiAlternatives()
#                 email.subject = f"Attention Required: Late Entry Logged {current_date}"
#                 email.attach_alternative(html_body, "text/html")
#                 email.to = [employee.email]
#                 email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
#                 email.send()


# def late_attendance_calculate(late_entry_time=None):
#     employees = Employee.objects.filter(
#         active=True, show_in_attendance_list=True, exception_la=False  #exception_la = exception_late_attendance if true then thats are not counted as late
#     ).exclude(salaryhistory__isnull=True)
#     late_entry = late_entry_time if late_entry_time else time(hour=11, minute=11)

#     current_date = datetime.now()
#     current_month = current_date.month
#     current_year = current_date.year

#     for employee in employees:
#         total_consider = LateAttendanceFine.objects.filter(
#             employee=employee,
#             date__year=current_year,
#             date__month=current_month,
#             is_consider=True,
#         ).count()

#         # Count late entries for the current month
#         total_late_entry = (
#             EmployeeAttendance.objects.filter(
#                 employee=employee,
#                 date__year=current_year,
#                 date__month=current_month,
#                 entry_time__gt=late_entry,
#             ).count()
#             - total_consider
#         )

#         # Check if there is a late entry for today
#         today_late_entry = EmployeeAttendance.objects.filter(
#             employee=employee, date=current_date, entry_time__gt=late_entry
#         )

#         if not LateAttendanceFine.objects.filter(
#             employee=employee, date=current_date
#         ).exists() and today_late_entry.exists():
#             entry_time = today_late_entry.first().entry_time
#             late_count = total_late_entry + 1  # Include today's late entry

#             if total_late_entry > 6:
#                 fine_amount = 500.00
#             elif total_late_entry > 3:
#                 fine_amount = 80.00
#             else:
#                 fine_amount = 0.00

#             LateAttendanceFine.objects.create(
#                 employee=employee,
#                 month=current_month,
#                 year=current_year,
#                 date=current_date,
#                 is_consider=False,
#                 total_late_attendance_fine=fine_amount,
#                 entry_time=entry_time,
#             )

#             html_body = loader.render_to_string(
#                 "mails/late_entry_mail.html",
#                 context={
#                     "employee": employee,
#                     "entry_time": entry_time,
#                     "late_count": late_count,
#                 },
#             )
#             email = EmailMultiAlternatives(
#                 subject=f"Attention Required: Late Entry Logged {current_date}",
#                 from_email='"Mediusware-HR" <hr@mediusware.com>',
#                 to=[employee.email],
#             )
#             email.attach_alternative(html_body, "text/html")
#             try:
#                 email.send()
#             except Exception as e:
#                 # Log the error (e.g., using logging module) instead of raising
#                 print(f"Failed to send email to {employee.email}: {str(e)}")





def late_attendance_calculate(late_entry_time=None):
    employees = Employee.objects.filter(
        active=True, show_in_attendance_list=True, exception_la=False   
    ).exclude(salaryhistory__isnull=True)
    late_entry = late_entry_time if late_entry_time else time(hour=11, minute=11)

    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    for employee in employees:
        # Get considered late entries for current month
        total_consider = LateAttendanceFine.objects.filter(
            employee=employee,
            date__year=current_year,
            date__month=current_month,
            is_consider=True,
        ).count()

        # Count late entries for current month (including today)
        total_late_entry = (
            EmployeeAttendance.objects.filter(
                employee=employee,
                date__year=current_year,
                date__month=current_month,
                entry_time__gt=late_entry,
            ).count()
            - total_consider
        )

        # Check today's late entry
        today_late_entry = EmployeeAttendance.objects.filter(
            employee=employee, date=current_date, entry_time__gt=late_entry
        )

        if not LateAttendanceFine.objects.filter(
            employee=employee, date=current_date
        ).exists() and today_late_entry.exists():
            entry_time = today_late_entry.first().entry_time
            # Use total_late_entry directly (already includes today)
            late_count = total_late_entry  # FIX: Removed +1

            if total_late_entry > 6:
                fine_amount = 500.00
            elif total_late_entry > 3:
                fine_amount = 80.00
            else:
                fine_amount = 0.00

            LateAttendanceFine.objects.create(
                employee=employee,
                month=current_month,
                year=current_year,
                date=current_date,
                is_consider=False,
                total_late_attendance_fine=fine_amount,
                entry_time=entry_time,
            )

            html_body = loader.render_to_string(
                "mails/late_entry_mail.html",
                context={
                    "employee": employee,
                    "entry_time": entry_time,
                    "late_count": late_count,
                },
            )
            email = EmailMultiAlternatives(
                subject=f"Attention Required: Late Entry Logged {current_date}",
                from_email='"Mediusware-HR" <hr@mediusware.com>',
                to=[employee.email],
            )
            email.attach_alternative(html_body, "text/html")
            try:
                email.send()
            except Exception as e:
                print(f"Failed to send email to {employee.email}: {str(e)}")


def send_birthday_email():
    employees = Employee.objects.filter(
        active=True, date_of_birth=timezone.now().date()
    )

    for employee in employees:
        html_body = loader.render_to_string(
            "mails/employee_birthday_mail.html",
            context={
                "employee": employee,
            },
        )

        email = EmailMultiAlternatives()
        email.subject = "Happy Birthday!"
        email.attach_alternative(html_body, "text/html")
        email.to = [employee.email]
        email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
        email.send()


from django.db.models import DateTimeField, Max, Value
from django.db.models.functions import Coalesce


def new_late_attendance_calculate(late_entry_time):
    late_entry = time(hour=11, minute=31)
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    # Annotate late entry time for today using aggregate
    employees = (
        Employee.objects.filter(active=True, show_in_attendance_list=True)
        .exclude(salaryhistory__isnull=True)
        .annotate(
            total_consider=Count(
                "lateattendancefine",
                filter=Q(
                    lateattendancefine__date__year=current_year,
                    lateattendancefine__date__month=current_month,
                    lateattendancefine__is_consider=True,
                ),
            ),
            total_late_entry=Count(
                "employeeattendance",
                filter=Q(
                    employeeattendance__date__year=current_year,
                    employeeattendance__date__month=current_month,
                    employeeattendance__entry_time__gt=late_entry_time,
                ),
            )
            - F("total_consider"),
            today_late_entry_time=Coalesce(
                Max(
                    "employeeattendance__entry_time",
                    filter=Q(
                        employeeattendance__date=current_date,
                        employeeattendance__entry_time__gt=late_entry,
                    ),
                ),
                Value(None),
                output_field=DateTimeField(),
            ),
            has_today_fine=Count(
                "lateattendancefine",
                filter=Q(lateattendancefine__date=current_date),
            ),
        )
    )

    # Filter employees
    late_employees = employees.filter(
        today_late_entry_time__isnull=False, has_today_fine=0
    )

    # Prepare fines and emails
    fines = []
    emails = []

    for employee in late_employees:
        fine_amount = 0.00
        if employee.total_late_entry > 6:
            fine_amount = 500.00
        elif employee.total_late_entry > 3:
            fine_amount = 80.00

        fines.append(
            LateAttendanceFine(
                employee=employee,
                month=current_month,
                year=current_year,
                date=current_date,
                total_late_attendance_fine=fine_amount,
                entry_time=employee.today_late_entry_time,
                is_consider=False,
            )
        )

        if fine_amount > 0:
            html_body = loader.render_to_string(
                "mails/late_entry_mail.html",
                context={
                    "employee": employee,
                    "entry_time": employee.today_late_entry_time,
                },
            )
            email = EmailMultiAlternatives()
            email.subject = f"Attention Required: Late Entry Logged {current_date}"
            email.attach_alternative(html_body, "text/html")
            email.to = [employee.email]
            email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
            emails.append(email)

    # Bulk create fines
    LateAttendanceFine.objects.bulk_create(fines)
    print(fines)
    print("Fines created.")
    # Send emails
    for email in emails:
        email.send()


def send_resignation_application_email(obj):
    body = f"""
        Dear HR Team,

        This is to inform you that {obj.employee.full_name}, currently working as {obj.employee.designation}, has submitted their resignation on {obj.date}.

        Please Review the resignation application on HR Portal.

        Best regards,
        {obj.employee.full_name}
        
        """
    email = EmailMessage(
        subject=f"Resignation Application From {obj.employee.full_name}",
        body=body,
        from_email=obj.employee.email,
        to=["hr@mediusware.com"],
    )
    email.send()


def send_resignation_feedback_email(subject, body, from_email, to_email):
    email = EmailMultiAlternatives()
    email.subject = subject
    email.attach_alternative(body, "text/html")
    email.to = to_email
    email.from_email = from_email
    email.send()




def email_send_to_employee(employee, pdf, html_body, subject):
    email = EmailMultiAlternatives()
    email.subject = subject
    email.attach_alternative(html_body, "text/html")
    email.to = [employee.email]
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    if pdf and pdf.__contains__("http"):
        pdf_url = pdf
        response = requests.get(pdf_url)
        email.attach(pdf.split("/")[-1], response.content, "application/pdf")
    elif pdf:
        email.attach_file(pdf)
    email.send()
    
    
    
def role_change_email_send_to_employee(employee, pdf, html_body, subject):
    email = EmailMultiAlternatives()
    email.subject = subject
    email.attach_alternative(html_body, "text/html")
    email.to = [employee.email]
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    if pdf and pdf.__contains__("http"):
        pdf_url = pdf
        response = requests.get(pdf_url)
        email.attach(pdf.split("/")[-1], response.content, "application/pdf")
    elif pdf:
        email.attach_file(pdf)
    email.send()


def send_absent_without_leave_email():
    """
    Sends an email to HR with a list of employees who are absent without leave for today
    and creates system-generated leave applications in bulk.
    """
    today = datetime.now()
    print(today.strftime("%A"))
    
    # if today.strftime("%A") == "Friday":
    if today.strftime("%A") == "Saturday" or today.strftime("%A") == "Sunday":
        return

    # Query to get employee IDs who are on leave today
    employees_on_leave = Leave.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status__in=['approved', 'pending']
    ).values_list('employee_id', flat=True)

    # Query to get employee IDs with attendance today
    employees_with_attendance = EmployeeAttendance.objects.filter(
        date=today
    ).values_list('employee_id', flat=True)

    # Get active employees who are neither on leave nor have attendance
    absent_employees = Employee.objects.filter(
        active=True
    ).exclude(
        user__is_superuser=True
    ).exclude(
        id__in=employees_on_leave
    ).exclude(
        show_in_attendance_list=False
    ).exclude(
        id__in=employees_with_attendance
    ).only('id', 'full_name', 'phone')  # Optimize by fetching only needed fields

    # Get system user for creating leave applications
    system_user = User.objects.filter(is_superuser=True).first()

    # if not absent_employees.exists():
    #     return

    # Prepare leave objects and employee names using comprehensions
    leave_objects = [
        Leave(
            employee=employee,  # Use employee object directly
            start_date=today,
            end_date=today,
            # leave_type='system_generated',
            applied_leave_type='system_generated',
            total_leave=1.0,
            note=f"System-generated leave for absence on {today}",
            message=f"Automatically generated leave application for {employee.full_name} due to absence without leave on {today}.",
            created_by=system_user,
            status='pending'
        ) for employee in absent_employees
    ]
    employee_data = [{'name': employee.full_name, 'phone': employee.phone} for employee in absent_employees]

    # Bulk create leave applications
    if leave_objects:
        Leave.objects.bulk_create(leave_objects)

    # Prepare and send the email
    html_body = loader.render_to_string(
        "mails/absent_without_leave.html",
        context={
            "employees": employee_data,  # Pass list of dicts with name and phone
            "total_employees": len(employee_data),
            "date": today,
        },
    )

    email = EmailMultiAlternatives(
        subject=f"Employees Absent Without Leave on {today}",
        from_email='"Mediusware-HR" <hr@mediusware.com>',
        to=["hr@mediusware.com"],
    )
    print("email body")
    email.attach_alternative(html_body, "text/html")
    print("email body end")
    email.send()
    print(f"Email sent to HR with {len(employee_data)} absent employees for {today}.")