from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery


def formal_summery(request):
    employee_formal_summery = EmployeeNearbySummery()
    return {
        "leaves": employee_formal_summery.employee_leave_nearby,
        "birthdays": employee_formal_summery.birthdays,
        "increments": employee_formal_summery.increments,
        "permanents": employee_formal_summery.permanents,
        "anniversaries": employee_formal_summery.anniversaries
    }
