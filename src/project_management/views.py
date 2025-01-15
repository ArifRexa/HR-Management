from django.http import JsonResponse
from datetime import datetime, timedelta
from weasyprint import HTML
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone

from django.db.models import Q, F, Aggregate, CharField


from project_management.models import DailyProjectUpdate, Project, ProjectHour
from project_management.utils.auto_client_weekly_report import ClientWeeklyUpdate


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
    project_hour_id = request.GET.get("project_hour_id")
    manager_id = request.user.employee.id
    if project_hour_id:
        manager_id = ProjectHour.objects.get(id=project_hour_id).manager_id

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
    d = DailyProjectUpdate.objects.filter(
        q_obj,
        employee__active=True,
        employee__project_eligibility=True,
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
        .values(
            "id",
            "created_at",
            "employee_id",
            "full_name",
            "hours",
            "update",
            "updates_json",
        )
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


def generate_client_weekly_report(request, project_id, hour_date):
    project_hour_id = request.GET.get("project_hour_id")
    manager_id = request.user.employee.id
    if project_hour_id:
        manager_id = ProjectHour.objects.get(id=project_hour_id).manager_id

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
        .values(
            "id",
            "update",
            "updates_json",
        )
    )
    update = "\n\n".join([i["updates_json"][0][0] for i in employee])
    open_ai_res = ClientWeeklyUpdate(update)
    data = open_ai_res.chat()
    if not data:
        return JsonResponse(
            {"status": 500, "state": "AI can't generate report from given data"}
        )
    template_name = "admin/client_weekly_report.html"
    template = get_template(template_name)
    context = {
        "reports": data,
        "project": Project.objects.get(id=project_id),
        "start_date": hour_date,
        "end_date": hour_date - timedelta(days=6),
    }
    html_content = template.render(context)

    # Generate PDF
    html = HTML(string=html_content)
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    # filename = str(timezone.now())
    # response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return response
