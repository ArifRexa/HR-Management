from django.db.models import Count, F, ExpressionWrapper, Q, BooleanField
from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery
from employee.forms.employee_online import EmployeeStatusForm
from employee.forms.employee_project import EmployeeProjectForm
from employee.models import EmployeeOnline
from employee.models.employee_activity import EmployeeProject


def formal_summery(request):
    employee_ids = [7, 30, 76, 49]
    employee_formal_summery = EmployeeNearbySummery()
    employee_offline = EmployeeOnline.objects.filter(
        employee__active=True).order_by('active', 'employee__full_name').exclude(employee_id__in=employee_ids).all()
    employee_projects = EmployeeProject.objects.filter(
        employee__active=True).annotate(project_exists=ExpressionWrapper(
                                            Count("project"),
                                            output_field=BooleanField()
                                        )
                                ).order_by('project_exists', 'employee__full_name'
                                ).exclude(employee_id__in=employee_ids).all()

    return {
        "leaves": employee_formal_summery.employee_leave_nearby,
        "birthdays": employee_formal_summery.birthdays,
        "increments": employee_formal_summery.increments,
        "permanents": employee_formal_summery.permanents,
        "anniversaries": employee_formal_summery.anniversaries,
        'employee_offline': employee_offline,
        "employee_projects": employee_projects
    }


def employee_status_form(request):
    if request.user.is_authenticated:
        employee_online = EmployeeOnline.objects.get(employee_id=request.user.employee.id)
        return {
            'status_form': EmployeeStatusForm(instance=employee_online)
        }
    else:
        return {
            'status_form': EmployeeStatusForm()
        }


def employee_project_form(request):
    if request.user.is_authenticated:
        employee_project = EmployeeProject.objects.get(employee_id=request.user.employee.id)
        return {
            'employee_project_form': EmployeeProjectForm(instance=employee_project)
        }
    else:
        return {
            'employee_project_form': EmployeeProjectForm()
        }
