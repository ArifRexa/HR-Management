from datetime import timedelta

from django.contrib import admin
from django.db.models import Q, Sum
from django.template.loader import get_template
from django.utils.html import format_html

from employee.models import Employee

# from networkx import project
from employee.models.employee import EmployeeUnderTPM
from project_management.models import (
    Client,
    DailyProjectUpdate,
    Project,
    ProjectHour,
    ProjectHourHistry,
)


class ProjectFilter(admin.SimpleListFilter):
    title = "Project"
    parameter_name = "project__id__exact"
    template = "admin/project_management/project_filter.html"

    def lookups(self, request, model_admin):
        project_types = (
            Project.objects.filter(active=True)
            .values_list("id", "title", "client__name")
            .distinct()
        )
        choices = []
        for project_id, project_title, client_name in project_types:
            display_name = (
                f"{project_title} ({client_name})"
                if client_name
                else project_title
            )
            choices.append((str(project_id), display_name))
        return choices

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(
                remove=[self.parameter_name]
            ),
            "display": ("All"),
        }

        for lookup, title in self.lookup_choices:
            project = Project.objects.get(pk=lookup)
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": format_html(
                    f'<span style="color: red;">{title}</span>'
                )
                if not project.check_is_weekly_project_hour_generated
                else format_html(
                    f'<span style="color: inherit;">{title}</span>'
                ),
            }

    def queryset(self, request, queryset):
        project_id = self.value()
        if project_id:
            return queryset.filter(
                project__id=project_id,
            )
        else:
            return queryset


class ProjectTypeFilter(admin.SimpleListFilter):
    title = "hour type"
    parameter_name = "hour_type"

    def lookups(self, request, model_admin):
        return (("bonus", "Bonus"), ("project", "Project"))

    def queryset(self, request, queryset):
        if self.value() == "bonus":
            return queryset.filter(
                hour_type="bonus",
            )
        elif self.value() == "project":
            return queryset.filter(
                hour_type="project",
            )


class ProjectManagerFilter(admin.SimpleListFilter):
    title = "manager"
    parameter_name = "manager__id__exact"

    def lookups(self, request, model_admin):
        employees = Employee.objects.filter(active=True, manager=True).values(
            "id", "full_name"
        )
        return tuple(
            [
                (
                    emp.get("id"),
                    emp.get("full_name"),
                )
                for emp in employees
            ]
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(manager__id__exact=self.value())


class ProjectLeadFilter(admin.SimpleListFilter):
    title = "lead"
    parameter_name = "manager__id__exact"

    def lookups(self, request, model_admin):
        employees = Employee.objects.filter(active=True, lead=True).values(
            "id", "full_name"
        )
        return tuple(
            [
                (
                    emp.get("id"),
                    emp.get("full_name"),
                )
                for emp in employees
            ]
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(manager__id__exact=self.value())


class ProjectClientFilter(admin.SimpleListFilter):
    title = "client"
    parameter_name = "project__client__id__exact"

    def lookups(self, request, model_admin):
        employees = (
            Client.objects.filter(project__active=True)
            .distinct()
            .values("id", "name")
        )
        return tuple(
            [
                (
                    emp.get("id"),
                    emp.get("name"),
                )
                for emp in employees
            ]
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(project__client__id__exact=self.value())


class TPMProjectFilter(admin.SimpleListFilter):
    title = "TPM"
    parameter_name = "tpm_id__exact"

    def lookups(self, request, model_admin):
        employees = (
            Employee.objects.filter(active=True, is_tpm=True)
            .distinct()
            .values("id", "full_name")
        )
        return tuple(
            [
                (
                    emp.get("id"),
                    emp.get("full_name"),
                )
                for emp in employees
            ]
        )

    def queryset(self, request, queryset):
        tpm_project = (
            EmployeeUnderTPM.objects.filter(
                tpm__id__exact=self.value(),
            )
            .values_list("project_id", flat=True)
            .distinct()
        )
        # employee_project = EmployeeProject.objects.filter(
        #     employee__id__exact=self.value()
        # )
        # project_list = (
        #     employee_project.first().project.values_list("id", flat=True)
        #     if employee_project.exists()
        #     else []
        # )
        if self.value():
            return queryset.filter(project_id__in=tpm_project)
        return queryset


class StatusFilter(admin.SimpleListFilter):
    title = "Status"
    parameter_name = "status__exact"

    def lookups(self, request, model_admin):
        STATUS_CHOICE = (("pending", "⌛ Pending"), ("approved", "✔ Approved"))
        return tuple([status for status in STATUS_CHOICE])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class ProjectHourOptions(admin.ModelAdmin):
    class Media:
        css = {"all": ("css/list.css",)}
        js = ("js/list.js", "js/update_project_hour.js")

    # override create / edit fields
    # manager filed will not appear if the authenticate user is not super user
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request)
        if not request.user.is_superuser:
            fields.remove("manager")
            fields.remove("payable")
            if not request.user.has_perm("project_management.select_hour_type"):
                fields.remove("hour_type")
            if not request.user.employee.is_tpm:
                fields.remove("status")
        return fields

    def get_readonly_fields(self, request, obj):
        return ["tpm"]

    def get_list_filter(self, request):
        filters = [
            ProjectTypeFilter,
            TPMProjectFilter,
            StatusFilter,
            ProjectFilter,
            "project__client__payment_method",
            "project__client__invoice_type",
            ProjectClientFilter,
            "manager",
        ]
        if not request.user.has_perm("project_management.view_client"):
            filters.remove("project__client__payment_method")
            filters.remove(ProjectClientFilter)
            filters.remove("project__client__invoice_type")
        return filters

    def get_list_display(self, request):
        """

        @type request: object
        """
        list_display = [
            "date",
            "project",
            "display_hours",
            "get_daily_update",
            "manager",
            "get_resources",
            "get_status",
        ]
        # if not request.user.is_superuser:
        #     list_display.remove('payable')
        return list_display

    def display_hours(self, obj):
        hours = (
            ProjectHourHistry.objects.filter(history__id=obj.id)
            .values_list("hour_history", flat=True)
            .order_by("-id")
        )
        if not hours:
            return obj.hours
        hours_list = []
        for index, hour in enumerate(hours):
            if index == 0:
                hours_list.append(f"<b style='font-size: 16px;'>{hour}</b>")
            else:
                hours_list.append(int(hour))

        return format_html("<br>".join(str(hour) for hour in hours_list))

    display_hours.short_description = "Hours"

    # @admin.display(description='Forcast', ordering='forcast')
    # def get_forcast(self, obj: ProjectHour):
    #     html_template = get_template('admin/project_hour/col_forcast.html')
    #     html_content = html_template.render({
    #         'project_hour': obj
    #     })
    #     return format_html(html_content)

    @admin.display(description="Daily Update")
    def get_daily_update(self, obj: ProjectHour):
        manager_id = obj.manager.id

        q_obj = Q(
            project=obj.id,
            manager=manager_id,
            created_at__date__lte=obj.date,
            created_at__date__gte=obj.date - timedelta(days=6),
        )
        employee = (
            DailyProjectUpdate.objects.filter(
                q_obj,
                employee__active=True,
                employee__project_eligibility=True,
            )
            .exclude(hours=0.0)
            .only(
                "hours",
            )
            .aggregate(total=Sum("hours"))
        )

        return employee.get("total", 0) if employee.get("total", None) else 0

    @admin.display(description="Resources")
    def get_resources(self, obj: ProjectHour):
        html = ""
        i = 1
        emp_list = {}
        for elem in obj.employeeprojecthour_set.all():
            if emp_list.get(elem.employee):
                emp_list[elem.employee] += elem.hours
            else:
                emp_list[elem.employee] = elem.hours

        for elem, hour in emp_list.items():
            if elem.sqa and hour > 10:
                html += f"<p>{i}.{elem.full_name} ({hour})</p>"
                i += 1
                continue
            html += f"<p>{i}.{elem.full_name} ({hour})</p>"
            i += 1
        return format_html(html)

    @admin.display(description="Approved By TPM")
    def get_status(self, obj):
        color = "red"
        if obj.status == "approved":
            color = "green"
        return format_html(
            f'<b style="color: {color}">{obj.get_status_display()}</b>'
        )

    @admin.display(description="Operation Feedback")
    def operation_feedback_link(self, obj):
        html_template = get_template(
            "admin/project_management/list/col_operation_feedback.html"
        )
        rendered_html = html_template.render({"obj": obj})
        return rendered_html

    @admin.display(description="Client Experience Feedback")
    def client_exp_feedback_link(self, obj):
        html_template = get_template(
            "admin/project_management/list/col_client_exp_feedback.html"
        )
        rendered_html = html_template.render({"obj": obj})
        return rendered_html

    # @admin.display(description='Project')
    # def get_project(self, obj: ProjectHour):
    #     return format_html(f'<div style="color: red;">{obj.project.title}</div>') if obj.project.check_is_weekly_project_hour_generated == False else format_html(f'<div style="color: inherit;">{obj.project.title}</div>')

    # def get_readonly_fields(self, request, obj=None):
    #     three_day_earlier = datetime.datetime.today() - datetime.timedelta(days=2)
    #     if obj is not None:
    #         print(obj.created_at)
    #         project_hour = ProjectHour.objects.filter(
    #             id=request.resolver_match.kwargs['object_id'],
    #             created_at__gte=three_day_earlier,
    #         ).first()
    #         if project_hour is None and not request.user.is_superuser:
    #             return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
    #     return ()
