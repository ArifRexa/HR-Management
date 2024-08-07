from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta

from employee.models import Employee
from django.db.models import Sum, Q, F, Aggregate, CharField
from django.db.models.functions import Coalesce

from project_management.models import DailyProjectUpdate


class GroupConcat(Aggregate):
    function = "GROUP_CONCAT"
    template = "%(function)s(%(distinct)s%(expressions)s%(ordering)s%(separator)s)"

    def __init__(
        self, expression, distinct=False, ordering=None, separator=",", **extra
    ):
        super().__init__(
            expression,
            distinct="DISTINCT " if distinct else "",
            ordering=" ORDER BY %s" % ordering if ordering is not None else "",
            separator=' SEPARATOR "%s"' % separator,
            output_field=CharField(),
            **extra,
        )


# Create your views here.
def get_this_week_hour(request, project_id, hour_date):
    manager_id = request.user.employee.id

    # employee = (
    #     Employee.objects.filter(active=True, project_eligibility=True)
    #     .annotate(
    #         total_hour=Coalesce(
    #             Sum(
    #                 "dailyprojectupdate_employee__hours",
    #                 filter=Q(
    #                     dailyprojectupdate_employee__project=project_id,
    #                     dailyprojectupdate_employee__manager=manager_id,
    #                     dailyprojectupdate_employee__status="approved",
    #                     dailyprojectupdate_employee__created_at__date__lte=hour_date,
    #                     dailyprojectupdate_employee__created_at__date__gte=hour_date
    #                     - timedelta(days=6),
    #                 ),
    #             ),
    #             0.0,
    #         ),
    #         update=F("dailyprojectupdate_employee__updates_json"),
    #         update_id=GroupConcat(F("dailyprojectupdate_employee__id")),
    #     )
    #     .exclude(total_hour=0.0)
    #     .values("id", "full_name", "total_hour", "update", "update_id")
    # )
    q_obj = Q(
        project=project_id,
        manager=manager_id,
        status="approved",
        created_at__date__lte=hour_date,
        created_at__date__gte=hour_date - timedelta(days=6),
    )
    employee = (
        DailyProjectUpdate.objects.filter(
            q_obj,
            employee__active=True,
            employee__project_eligibility=True,
        )
        .annotate(
            full_name=F("employee__full_name"),
        )
        .exclude(hours=0.0)
        .values("id", "employee_id", "full_name", "hours", "update", "updates_json")
    )

    totalHours = sum(hour["hours"] for hour in employee)

    employeeList = filter(lambda emp: emp["employee_id"], employee)

    data = {
        "manager_id": manager_id,
        "weekly_hour": list(employeeList),
        "total_project_hours": totalHours,
    }

    return JsonResponse(data)


def slack_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    return JsonResponse({"code": code, "state": state})
