from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery
from employee.forms.employee_online import EmployeeStatusForm
from employee.models import EmployeeOnline


def formal_summery(request):
    employee_formal_summery = EmployeeNearbySummery()
    employee_offline = EmployeeOnline.objects.filter(
        employee__active=True).order_by(
        'active', 'employee__full_name').exclude(
        employee_id__in=[7, 30, 76, 49]).all()
    return {
        "leaves": employee_formal_summery.employee_leave_nearby,
        "birthdays": employee_formal_summery.birthdays,
        "increments": employee_formal_summery.increments,
        "permanents": employee_formal_summery.permanents,
        "anniversaries": employee_formal_summery.anniversaries,
        'employee_offline': employee_offline
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
