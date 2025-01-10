from icecream import ic

from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Sum

from project_management.models import Project, DailyProjectUpdate, ProjectHour


# Create your views here.
def get_project_updates(request, project_hash):
    from_date, to_date = request.GET.get("fromdate"), request.GET.get("todate")
    ic(from_date, to_date)
    project_obj = Project.objects.filter(identifier=project_hash).first()
    daily_updates = DailyProjectUpdate.objects.filter(
        project=project_obj, status="approved", hours__gt=0
    ).select_related("employee", "manager", "project")

    if to_date and not from_date:
        daily_updates = daily_updates.filter(
            created_at__date__lte=to_date,
        )

    elif from_date and not to_date:
        daily_updates = daily_updates.filter(created_at__date__gte=from_date)
    elif from_date and to_date:
        daily_updates = daily_updates.filter(
            created_at__date__lte=to_date, created_at__date__gte=from_date
        )

    distinct_dates = daily_updates.values("created_at__date").distinct()[::-1]

    daily_update_list = []
    total_hour = 0
    if project_obj.is_team:
        print("team")
        for u_date in distinct_dates:
            obj = {"created_at": u_date.get("created_at__date").strftime("%d-%b-%Y")}
            updates = []
            time = 0
            update_objects = daily_updates.filter(
                created_at__date=u_date.get("created_at__date")
            )
            row_span = 0
            employee_id = None
            for update in update_objects:
                deleted_update_json = []
                if update.updates_json:
                    for json_1 in update.updates_json:
                        json_hour = float(json_1[1])
                        print(json_hour)
                    #     if json_hour == 0.0:
                    #         deleted_update_json.append(json_1)
                    # for delt in deleted_update_json:
                    #     update.updates_json.remove(delt)

                if employee_id == update.employee.id:
                    if update.updates_json is not None:
                        updates[-1]["update"] += update.updates_json
                        row_span += len(update.updates_json)
                        time += update.hours
                    else:
                        updates[-1]["update"] += [[update.update, update.hours]]
                        row_span += 1
                        time += update.hours
                else:
                    employee_id = update.employee.id

                    if update.updates_json is not None:
                        updates.append(
                            {
                                "update": update.updates_json,
                                "update_by": update.employee.full_name,
                                "hours": update.hours,
                            }
                        )
                        row_span += len(update.updates_json)
                        time += update.hours
                    else:
                        updates.append(
                            {
                                "update": [[update.update, update.hours]],
                                "update_by": update.employee.full_name,
                                "hours": update.hours,
                            }
                        )
                        row_span += 1
                        time += update.hours
            obj["update"] = updates
            obj["total_hour"] = time
            obj["row_span"] = row_span
            total_hour += time
            daily_update_list.append(obj)

        # ic(daily_update_list)
        # print(daily_update_list)
        paginator = Paginator(daily_update_list, 10)
        page_obj = paginator.get_page(request.GET.get("page"))

        out_dict = {
            "total_hour": total_hour,
            "project": project_obj,
            "daily_updates": page_obj,
        }
        return render(request, "client_management/project_details.html", out_dict)
    else:
        print("team not length of distinct dates", len(distinct_dates))

        for u_date in distinct_dates:
            obj = {"created_at": u_date.get("created_at__date").strftime("%d-%b-%Y")}
            updates = []
            time = 0
            update_objects = daily_updates.filter(
                created_at__date=u_date.get("created_at__date")
            )
            for update in update_objects:
                deleted_update_json = []
                if update.updates_json:
                    for json_1 in update.updates_json:
                        json_hour = float(json_1[1])
                        print(json_hour)
                    #     if json_hour == 0.0:
                    #         deleted_update_json.append(json_1)
                    # for delt in deleted_update_json:
                    #     update.updates_json.remove(delt)

                if update.updates_json is not None:
                    updates.extend(update.updates_json)
                    time += update.hours
                else:
                    updates.extend([[update.update, update.hours]])
                    time += update.hours
            obj["update"] = updates
            obj["total_hour"] = time
            total_hour += time
            daily_update_list.append(obj)

        # ic(daily_update_list)

        paginator = Paginator(daily_update_list, 10)
        page_obj = paginator.get_page(request.GET.get("page"))

        out_dict = {
            "total_hour": total_hour,
            "project": project_obj,
            "daily_updates": page_obj,
        }

        return render(request, "client_management/project_details.html", out_dict)


def get_weekly_project_report(request, project_hash):
    from_date, to_date = request.GET.get("fromdate"), request.GET.get("todate")
    ic(from_date, to_date)
    project_obj = Project.objects.filter(identifier=project_hash).first()
    
    project_hour = ProjectHour.objects.filter(project=project_obj).order_by("-date").only(
        'date', 'hours', 'report_file'
    )
    paginator = Paginator(project_hour, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        'weekly_reports': page_obj,
        "total_hour": project_hour.aggregate(total_hour=Sum("hours")).get("total_hour", 0),
        "project": project_obj
    }
    return render(request, 'client_management/project_weekly_report.html', context)