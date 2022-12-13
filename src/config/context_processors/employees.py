from django.db.models import Count, F, ExpressionWrapper, Q, BooleanField, Case, When, Value, Min
from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery
from employee.forms.employee_online import EmployeeStatusForm
from employee.forms.employee_project import EmployeeProjectForm
from employee.models import EmployeeOnline
from employee.models.employee_activity import EmployeeProject
from config.settings import employee_ids


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
        employee_projects = employee_projects.order_by('project_exists', order_keys.get(order_by, '1'))

    return {
        "leaves": employee_formal_summery.employee_leave_nearby,
        "birthdays": employee_formal_summery.birthdays,
        "increments": employee_formal_summery.increments,
        "permanents": employee_formal_summery.permanents,
        "anniversaries": employee_formal_summery.anniversaries,
        'employee_offline': employee_offline,
        "employee_projects": employee_projects,
        "ord": order_by,
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
