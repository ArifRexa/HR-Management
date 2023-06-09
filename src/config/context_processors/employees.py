from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, BooleanField, Case, When, Value, Min, Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from config.settings import employee_ids

from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery
from employee.forms.employee_online import EmployeeStatusForm
from employee.forms.employee_project import EmployeeProjectForm
from employee.models import EmployeeOnline, Leave
from employee.models.employee_activity import EmployeeProject
from employee.models.employee_feedback import EmployeeFeedback
from employee.models.employee import Employee
from employee.models import FavouriteMenu

from settings.models import Announcement

from datetime import datetime




def formal_summery(request):
    employee_formal_summery = EmployeeNearbySummery()

    leaves_nearby, leaves_nearby_count  = employee_formal_summery.employee_leave_nearby()


    # employee_offline = EmployeeOnline.objects.filter(
    #     employee__active=True
    # ).order_by(
    #     '-employee__need_cto', 
    #     '-employee__need_hr', 
    #     'active', 
    #     'employee__full_name'
    # ).exclude(
    #     employee_id__in=employee_ids
    # )

    # employee_projects = EmployeeProject.objects.filter(
    #     employee__active=True, employee__project_eligibility=True
    # ).annotate(
    #     project_count=Count("project"),
    #     project_order=Min("project"),
    #     project_exists=Case(
    #         When(project_count=0, then=Value(False)),
    #         default=Value(True),
    #         output_field=BooleanField()
    #     )
    # ).order_by('project_exists', 'employee__full_name').exclude(employee_id__in=employee_ids).all()

    # order_keys = {
    #     '1': 'employee__full_name',
    #     '-1': '-employee__full_name',
    #     '2': 'project_order',
    #     '-2': '-project_order',
    # }

    # order_by = request.GET.get('ord', None)
    # if order_by:
    #     order_by_list = ['project_exists', order_keys.get(order_by, '1')]
    #     if order_by not in ['1', '-1']:
    #         order_by_list.append('employee__full_name')

    #     employee_projects = employee_projects.order_by(*order_by_list)
    
    # current_month_feedback_done = False
    # if not isinstance(request.user, AnonymousUser):
    #     if str(request.user.employee.id) in employee_ids:
    #         current_month_feedback_done = True
    #     else:
    #         current_month_feedback_done = EmployeeFeedback.objects.filter(
    #             employee=request.user.employee,
    #             created_at__date__month=timezone.now().date().month,
    #         ).exists()

    # return {
    #     "leaves": employee_formal_summery.employee_leave_nearby,
    #     "birthdays": employee_formal_summery.birthdays,
    #     "increments": employee_formal_summery.increments,
    #     "permanents": employee_formal_summery.permanents,
    #     "anniversaries": employee_formal_summery.anniversaries,
    #     'employee_offline': employee_offline,
    #     "employee_projects": employee_projects,
    #     "ord": order_by,
    #     "birthday_today": get_managed_birthday_image(request),
    #     "current_month_feedback_done": current_month_feedback_done,
    #     "announcement": get_announcement(request),
    # }

    return {
        "leaves": leaves_nearby,
        "leaves_count": leaves_nearby_count,

        "birthdays": [],
        "increments": [],
        "permanents": [],
        "anniversaries": [],
        'employee_offline': [],
        "employee_projects": [],
        "ord": [],
        "birthday_today": [],
        "current_month_feedback_done": [],
        "announcement": [],
    }


def employee_status_form(request):
    if request.user.is_authenticated and str(request.user.employee.id) not in employee_ids:
        employee_online = EmployeeOnline.objects.get(employee_id=request.user.employee.id)
        return {
            'status_form': EmployeeStatusForm(instance=employee_online)
        }
    else:
        return {
            'status_form': None
        }


def employee_project_form(request):
    if request.user.is_authenticated and not str(request.user.employee.id) in employee_ids:
        employee_project = EmployeeProject.objects.get(employee_id=request.user.employee.id)
        return {
            'employee_project_form': EmployeeProjectForm(instance=employee_project)
        }
    else:
        return {
            'employee_project_form': None
        }


def get_announcement(request):
    data = []
    now = timezone.now()

    # Get Announcements
    announcements = Announcement.objects.filter(
        is_active=True,
        start_datetime__lte=now, 
        end_datetime__gte=now,
    ).order_by(
        '-rank',
    )

    # Get CTO
    get_cto_needed = Employee.objects.filter(active=True, need_cto=True)
    if get_cto_needed.exists():
        cto_needers = [emp.full_name for emp in get_cto_needed]
        cto_needers_text = ', '.join(cto_needers)
        data.append(f"{cto_needers_text} need{'s' if len(cto_needers)==1 else ''} the CTO's help.")
    
    # Get HR
    get_hr_needed = Employee.objects.filter(active=True, need_hr=True)
    if get_hr_needed.exists():
        hr_needers = [emp.full_name for emp in get_hr_needed]
        hr_needers_text = ', '.join(hr_needers)
        data.append(f"{hr_needers_text} need{'s' if len(hr_needers)==1 else ''} the HR's help.")

    # Announcements
    if announcements.exists():
        data.extend(announcement.description for announcement in announcements)

    # Get Leaves
    leaves_today = Leave.objects.filter(
        start_date__lte=now, end_date__gte=now,
    ).exclude(
        status='rejected',
    ).select_related(
        'employee',
    )
    if leaves_today.exists():
        leaves = [(leave.employee.full_name, dict(Leave.LEAVE_CHOICE).get(leave.leave_type),) for leave in leaves_today]
        for leave in leaves:
            data.append(f"{leave[0]} is on {leave[1]} today.")
    
    # Get Birthdays
    birthdays_today = Employee.objects.filter(active=True, date_of_birth__day=now.date().day, date_of_birth__month=now.date().month)
    if birthdays_today.exists():
        birthdays = [emp.full_name for emp in birthdays_today]
        birthdays_text = ', '.join(birthdays)
        data.append(f"{birthdays_text} {'has' if len(birthdays)==1 else 'have'} birthday today.")
    
    # Format Data
    if data:
        initial = f'<span style="background-color:tomato;padding:0.4rem 0.8rem;border-radius:0.4rem;">ANNOUNCEMENTS</span> {"&nbsp;"*8}🚨'
        data = initial + f' {"&nbsp;"*8}🚨'.join(
            [f'<span class="single_announcement">{d}</span>' for d in data]
        )
        data = format_html(data)

    return data if data else None


def get_managed_birthday_image(request):
    path = request.get_full_path()
    if not path == '/admin/':
        return False

    if isinstance(request.user, AnonymousUser):
        birthday = False
    else:
        birthday = False
        if request.user.employee.date_of_birth == datetime.today().date():
            if not request.user.employee.birthday_image_shown:
                try:
                    birthday = request.user.employee.birthday_image.url
                except:
                    birthday = False
                Employee.objects.filter(user=request.user).update(birthday_image_shown=True)
            else:
                Employee.objects.filter(user=request.user).update(birthday_image_shown=False)
    return birthday


def favourite_menu_list(request):
    if request.user.is_authenticated and request.user.employee is not None:
        f_menu = FavouriteMenu.objects.filter(employee_id=request.user.employee.id)
        data = {}
        data['object_list'] = f_menu
        return data
    return []
    
        
