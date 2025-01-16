import datetime
import json
from datetime import timedelta

from django.contrib import admin

from django.core.exceptions import ValidationError
from django import forms

# Register your models here.
from django.db.models import Sum, Q, F
from django.shortcuts import redirect
from django.template.context_processors import request
from django.utils import timezone
from django.template.loader import get_template
from django.utils.html import format_html
from config.admin import ExportCsvMixin, RecentEdit
from config.admin.utils import simple_request_filter
from employee.models.employee import EmployeeUnderTPM
from employee.models.employee_activity import EmployeeProject
from project_management.admin.project_hour.actions import ProjectHourAction
from project_management.admin.project_hour.options import ProjectHourOptions
from project_management.forms import ProjectHourFilterForm
from project_management.models import (
    Client,
    DailyProjectUpdate,
    Project,
    ProjectHour,
    EmployeeProjectHour,
)


class EmployeeHourInlineForm(forms.ModelForm):
    date = forms.DateTimeField(required=False)
    update_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    update = forms.CharField(required=False, widget=forms.Textarea())

    class Meta:
        model = EmployeeProjectHour
        fields = ("date", "hours", "employee")

    def save(self, commit):
        update_id = self.cleaned_data.get("update_id")
        update = self.cleaned_data.get("update")
        if update_id and update:
            daily_update = DailyProjectUpdate.objects.get(id=update_id)
            daily_update.updates_json = [[update, "0.0", ""]]
            daily_update.save()
        return super().save(commit)


class EmployeeHourAdmin(admin.TabularInline):
    model = EmployeeProjectHour
    extra = 1
    autocomplete_fields = ("employee",)
    form = EmployeeHourInlineForm

    def get_readonly_fields(self, request, obj=None):
        three_day_earlier = timezone.now() - timedelta(days=2)

        if obj is not None:
            tpm_project = EmployeeUnderTPM.objects.filter(
                project=obj.project, tpm=request.user.employee
            )
            if tpm_project.exists():
                return ()
            if obj.created_at <= three_day_earlier and not request.user.is_superuser:
                return (
                    "hours",
                    "employee",
                )
        return ()


class ProjectHourAdminForm(forms.ModelForm):
    def clean(self):
        data = super(ProjectHourAdminForm, self).clean()
        if data.get("hour_type") != "bonus":
            if self.request:
                if self.request.path_info[-5:-1] == "/add":
                    project = data.get("project")
                    if (
                        project
                        and ProjectHour.objects.filter(
                            manager_id=self.request.user.employee.id,
                            project_id=project.id,
                            date=data.get("date"),
                        ).exists()
                    ):
                        raise ValidationError(
                            {
                                "date": "Project Hour for this date with this project and manager already exists",
                            }
                        )
        path_info_list = [
            item for item in self.request.path_info.split("/") if item != ""
        ]
        if path_info_list[-1] == "/change":
            if self.request and not self.request.user.is_superuser:
                if (
                    self.request.user.employee.is_tpm
                    and not EmployeeUnderTPM.objects.filter(
                        tpm=self.request.user.employee, project=data.get("project")
                    ).exists()
                ):
                    raise ValidationError("You are not assign TPM for this project")
        return data


@admin.register(ProjectHour)
class ProjectHourAdmin(
    ProjectHourAction, ProjectHourOptions, RecentEdit, admin.ModelAdmin
):
    date_hierarchy = "date"
    search_fields = ["hours", "manager__full_name", "project__title", "date"]
    inlines = (EmployeeHourAdmin,)
    change_list_template = "admin/total.html"
    autocomplete_fields = ["project"]
    list_per_page = 50
    ordering = ("-pk",)
    add_form_template = "admin/project_hour/project_hour.html"
    change_form_template = "admin/project_hour/change_form.html"
    fieldsets = (
        (
            "Standard info",
            {"fields": ("hour_type", "project", "date", "hours", "report_file")},
        ),
        (
            "Administration Process",
            {"fields": ("tpm", "status")},
        ),
    )
    form = ProjectHourAdminForm

    def get_form(self, request, obj, change, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.request = request
        return form

    # query for get total hour by query string
    def get_total_hour(self, request):
        filter_data = simple_request_filter(request)
        if "tpm_id__exact" in request.GET:
            tpm_project = (
                EmployeeUnderTPM.objects.filter(
                    tpm__id__exact=request.GET.get("tpm_id__exact", 0),
                )
                .values_list("project_id", flat=True)
                .distinct()
            )
            filter_data.pop("tpm_id__exact")
            filter_data["project_id__in"] = list(tpm_project)
        qs = self.get_queryset(request).filter(**filter_data)
        if not request.user.is_superuser:
            qs.filter(manager__id__exact=request.user.employee.id)
        return qs.aggregate(tot=Sum("hours"))["tot"]

    def lookup_allowed(self, key, *args, **kwargs):
        if key in (
            "project__client__payment_method__id__exact",
            "project__client__id__exact",
            "project__client__invoice_type__id__exact",
            "project__client__invoice_type__isnull",
            "project__client__payment_method__isnull",
        ):
            return True
        return super(ProjectHourAdmin, self).lookup_allowed(key, *args, **kwargs)

    # override change list view
    # return total hour count
    def changelist_view(self, request, extra_context=None):
        from django.utils.http import urlencode

        # if not request.GET:
        #     # Redirect to the filtered view
        #     return redirect(f"{request.path}?{urlencode({'hour_type':'project'})}")
        my_context = dict(
            self.admin_site.each_context(request),
            total=self.get_total_hour(request),
            # series=self.get_data(request),
            filter_form=ProjectHourFilterForm(
                initial={
                    "created_at__date__gte": request.GET.get(
                        "created_at__date__gte",
                        timezone.now().date() - datetime.timedelta(days=7),
                    ),
                    "created_at__date__lte": request.GET.get(
                        "created_at__date__lte", timezone.now().date()
                    ),
                }
            ),
        )
        return super(ProjectHourAdmin, self).changelist_view(
            request, extra_context=my_context
        )

    def get_queryset(self, request):
        """Return query_set

        overrides django admin query set
        allow super admin only to see all project hour
        manager's will only see theirs
        @type request: object
        """
        if (
            request.GET.get("created_at__date__gte", None) is None
            and request.GET.get("q", None) is None
        ):
            two_month_ago = timezone.now() - timedelta(days=60)
            query_set = (
                super(ProjectHourAdmin, self)
                .get_queryset(request)
                .filter(created_at__gte=two_month_ago)
            )
        else:
            query_set = super(ProjectHourAdmin, self).get_queryset(request)

        if not request.GET:
            return query_set.filter(hour_type="project")
        if request.user.is_superuser or request.user.has_perm(
            "project_management.show_all_hours"
        ):
            return query_set
        return query_set.filter(manager_id=request.user.employee.id)

    def save_model(self, request, obj, form, change):
        """
        override project hour save
        manager id will be authenticate user employee id if the user is not super user
        """
        if not obj.manager_id:
            obj.manager_id = request.user.employee.id

        tpm_project = EmployeeUnderTPM.objects.filter(project=obj.project)
        if tpm_project.exists():
            obj.tpm = tpm_project.first().tpm
        else:
            obj.status = "approved"

        super(ProjectHourAdmin, self).save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj):
        fieldsets = super(ProjectHourAdmin, self).get_fieldsets(request, obj)

        if not request.user.employee.is_tpm:
            return (fieldsets[0],)
        if obj:
            tpm_project = EmployeeUnderTPM.objects.filter(
                tpm__id=request.user.employee.id,
                project=obj.project,
            )
            if not tpm_project.exists():
                return (fieldsets[0],)
        # if not request.user.has_perm("project_management.weekly_project_hours_approve"):
        #     return (fieldsets[0],)

        return fieldsets

    def get_data(self, request):
        print("*******************")
        print("get_data has called")
        series = list()
        selected_projects = (
            self.get_changelist_instance(request)
            .get_filters_params()
            .get("project__id__exact")
        )
        print("************** project id is *************", selected_projects)
        print("*** selected projects are ", selected_projects)
        if selected_projects:
            projects = Project.objects.filter(
                id__in=[selected_projects], active=True
            ).all()
        else:
            projects = Project.objects.filter(active=True).all()
        date_to_check = datetime.date.today() - datetime.timedelta(days=60)
        for project in projects:
            data = (
                project.projecthour_set.filter(date__gte=date_to_check)
                .annotate(date_str=F("date"))
                .extra(select={"date_str": "UNIX_TIMESTAMP(date)*1000"})
                .values("date_str")
                .annotate(total_hours=Sum("hours"))
                .values_list("date_str", "total_hours")
                .order_by("date_str")
            )

            print(data)
            # TODO : must be optimize otherwise it will effect the load time
            print("***************** data **************", data)
            array_date = []
            for value in data:
                array_date.append(list(value))

            series.append(
                {
                    "type": "spline",
                    # 'visible': 'false',
                    "name": project.title,
                    "data": list(array_date),
                }
            )
        if selected_projects:
            sum_hours = (
                ProjectHour.objects.filter(
                    project_id__in=selected_projects, date__gte=date_to_check
                )
                .extra(select={"date_str": "UNIX_TIMESTAMP(date)*1000"})
                .order_by("date")
                .values_list("date_str")
                .annotate(Sum("hours"))
            )

        else:
            sum_hours = (
                ProjectHour.objects.filter(date__gte=date_to_check)
                .extra(select={"date_str": "UNIX_TIMESTAMP(date)*1000"})
                .order_by("date")
                .values_list("date_str")
                .annotate(Sum("hours"))
            )
        sum_array = []
        # for sum_hour in sum_hours:
        #     sum_array.append(list(sum_hour)) #  it will return the total hours of projects.
        series.append(
            {"type": "spline", "name": "Total Project Hours", "data": sum_array}
        )
        # print('************** series ***********', series)
        return series

    # def get_data(self, request):
    #     series = []
    #     selected_projects = self.get_changelist_instance(request).get_filters_params().get('project__id__exact')
    #
    #     if selected_projects:
    #         projects = Project.objects.filter(id__in=selected_projects, active=True).all()
    #     else:
    #         projects = Project.objects.filter(active=True).all()
    #
    #     date_to_check = datetime.date.today() - datetime.timedelta(days=60)
    #
    #     for project in projects:
    #         data = project.projecthour_set.filter(date__gte=date_to_check).extra(
    #             select={'date_str': "UNIX_TIMESTAMP(date)*1000"}
    #         ).order_by('date').values_list('date_str', 'hours')
    #
    #         array_date = []
    #         for value in data:
    #             array_date.append(list(value))
    #
    #         series.append({
    #             'type': 'spline',
    #             'name': project.title,
    #             'data': list(array_date)
    #         })
    #
    #     # Calculate total project hours for filtered projects only
    #     if selected_projects:
    #         sum_hours = ProjectHour.objects.filter(project_id__in=selected_projects, date__gte=date_to_check).extra(
    #             select={'date_str': 'UNIX_TIMESTAMP(date)*1000'}
    #         ).order_by('date').values_list('date_str').annotate(Sum('hours'))
    #
    #         sum_array = []
    #         for sum_hour in sum_hours:
    #             sum_array.append(list(sum_hour))
    #
    #         series.append({
    #             'type': 'spline',
    #             'name': 'Total Project Hours',
    #             'data': sum_array
    #         })
    #
    #     return series
