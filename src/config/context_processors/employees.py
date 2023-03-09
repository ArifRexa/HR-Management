from django.db.models import Count, BooleanField, Case, When, Value, Min
from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery
from employee.forms.employee_online import EmployeeStatusForm
from employee.forms.employee_project import EmployeeProjectForm
from employee.models import EmployeeOnline
from employee.models.employee_activity import EmployeeProject
from employee.models.employee_feedback import EmployeeFeedback
from config.settings import employee_ids
from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from employee.models.employee import Employee
from employee.models import FavouriteMenu
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse

def formal_summery(request):
    employee_formal_summery = EmployeeNearbySummery()
    employee_offline = EmployeeOnline.objects.filter(
        employee__active=True).order_by('active', 'employee__full_name').exclude(employee_id__in=employee_ids).all()

    employee_projects = EmployeeProject.objects.filter(
        employee__active=True, employee__project_eligibility=True
    ).annotate(
        project_count=Count("project"),
        project_order=Min("project"),
        project_exists=Case(
            When(project_count=0, then=Value(False)),
            default=Value(True),
            output_field=BooleanField()
        )
    ).order_by('project_exists', 'employee__full_name').exclude(employee_id__in=employee_ids).all()

    order_keys = {
        '1': 'employee__full_name',
        '-1': '-employee__full_name',
        '2': 'project_order',
        '-2': '-project_order',
    }

    order_by = request.GET.get('ord', None)
    if order_by:
        order_by_list = ['project_exists', order_keys.get(order_by, '1')]
        if order_by not in ['1', '-1']:
            order_by_list.append('employee__full_name')

        employee_projects = employee_projects.order_by(*order_by_list)
    
    current_month_feedback_done = False
    if not isinstance(request.user, AnonymousUser):
        if str(request.user.employee.id) in employee_ids:
            current_month_feedback_done = True
        else:
            current_month_feedback_done = EmployeeFeedback.objects.filter(
                employee=request.user.employee,
                created_at__date__month=timezone.now().date().month,
            ).exists()

    return {
        "leaves": employee_formal_summery.employee_leave_nearby,
        "birthdays": employee_formal_summery.birthdays,
        "increments": employee_formal_summery.increments,
        "permanents": employee_formal_summery.permanents,
        "anniversaries": employee_formal_summery.anniversaries,
        'employee_offline': employee_offline,
        "employee_projects": employee_projects,
        "ord": order_by,
        "birthday_today": get_managed_birthday_image(request),
        "current_month_feedback_done": current_month_feedback_done,
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
    
        
