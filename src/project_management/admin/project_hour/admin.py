import datetime
from datetime import timedelta

from django.contrib import admin

from django.core.exceptions import ValidationError
from django import forms

# Register your models here.
from django.db.models import Sum, F, Prefetch

# from django.template.context_processors import request
from django.utils import timezone

from config.admin import RecentEdit
from config.admin.utils import simple_request_filter
from employee.models.employee import EmployeeUnderTPM
from project_management.admin.project_hour.actions import ProjectHourAction
from project_management.admin.project_hour.options import ProjectHourOptions
from project_management.forms import ProjectHourFilterForm
from project_management.models import (
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
    list_select_related = ("project", "manager")
    list_per_page = 50

    def get_form(self, request, obj, change, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.request = request
        return form

    # query for get total hour by query string
    def get_total_hour(self, request):
        filters = simple_request_filter(request)

        tpm_id = request.GET.get("tpm_id__exact")
        if tpm_id:
            project_ids = EmployeeUnderTPM.objects.filter(tpm_id=tpm_id).values_list("project_id", flat=True)
            filters.pop("tpm_id__exact")
            filters["project_id__in"] = list(project_ids)

        qs = self.get_queryset(request).filter(**filters)

        # if not request.user.is_superuser:
        #     qs = qs.filter(manager_id=request.user.employee.id)

        return qs.aggregate(total_hours=Sum("hours"))["total_hours"] or 0

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
        initial = {
            "created_at__date__gte": request.GET.get("created_at__date__gte", timezone.now().date() - timedelta(days=7)),
            "created_at__date__lte": request.GET.get("created_at__date__lte", timezone.now().date()),
        }

        extra_context = extra_context or {}
        extra_context.update({
            "total": self.get_total_hour(request),
            "filter_form": ProjectHourFilterForm(initial=initial),
        })

        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request) #.prefetch_related("projecthourhistory_set",Prefetch(
        #     "employeeprojecthour_set",
        #     queryset=EmployeeProjectHour.objects.select_related("employee") #.order_by("date"),
        # ))
        
        if not request.GET.get("created_at__date__gte") and not request.GET.get("q"):
            qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=60))
        
        if not request.GET:
            qs = qs.filter(hour_type="project")

        if request.user.is_superuser or request.user.has_perm("project_management.show_all_hours"):
            return qs
        
        return qs.filter(manager_id=request.user.employee.id)
    
    # def get_queryset(self, request):
    #     """Return query_set

    #     overrides django admin query set
    #     allow super admin only to see all project hour
    #     manager's will only see theirs
    #     @type request: object
    #     """
    #     if (
    #         request.GET.get("created_at__date__gte", None) is None
    #         and request.GET.get("q", None) is None
    #     ):
    #         two_month_ago = timezone.now() - timedelta(days=60)
    #         query_set = (
    #             super(ProjectHourAdmin, self)
    #             .get_queryset(request)
    #             .filter(created_at__gte=two_month_ago)
    #         )
    #     else:
    #         query_set = super(ProjectHourAdmin, self).get_queryset(request)

    #     if not request.GET:
    #         return query_set.filter(hour_type="project")
    #     if request.user.is_superuser or request.user.has_perm(
    #         "project_management.show_all_hours"
    #     ):
    #         return query_set
    #     return query_set.filter(manager_id=request.user.employee.id)

    def save_model(self, request, obj, form, change):
        if not obj.manager_id:
            obj.manager_id = request.user.employee.id

        tpm_record = EmployeeUnderTPM.objects.filter(project=obj.project).select_related("tpm").first()
        if tpm_record:
            obj.tpm = tpm_record.tpm
        else:
            obj.status = "approved"

        super().save_model(request, obj, form, change)

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
        print("******************* get_data has called")

        series = []
        date_to_check = datetime.date.today() - datetime.timedelta(days=60)

        # Extract selected project ID from filters
        selected_project_id = (
            self.get_changelist_instance(request)
            .get_filters_params()
            .get("project__id__exact")
        )

        print("************** Selected project id is *************", selected_project_id)

        # Filter projects
        if selected_project_id:
            projects = Project.objects.filter(id=selected_project_id, active=True)
        else:
            projects = Project.objects.filter(active=True)

        # Get project-wise series
        for project in projects:
            data = (
                project.projecthour_set
                .filter(date__gte=date_to_check)
                .annotate(date_str=F("date"))
                .extra(select={"date_str": "UNIX_TIMESTAMP(date)*1000"})  # Still using extra for JS compatibility
                .values("date_str")
                .annotate(total_hours=Sum("hours"))
                .values_list("date_str", "total_hours")
                .order_by("date_str")
            )

            array_date = [list(row) for row in data]

            series.append({
                "type": "spline",
                "name": project.title,
                "data": array_date,
            })

        # Prepare total project hour summary
        sum_query = ProjectHour.objects.filter(date__gte=date_to_check)
        if selected_project_id:
            sum_query = sum_query.filter(project_id=selected_project_id)

        sum_hours = (
            sum_query
            .extra(select={"date_str": "UNIX_TIMESTAMP(date)*1000"})
            .values("date_str")
            .annotate(total=Sum("hours"))
            .order_by("date_str")
            .values_list("date_str", "total")
        )

        sum_array = [list(row) for row in sum_hours]

        series.append({
            "type": "spline",
            "name": "Total Project Hours",
            "data": sum_array,
        })

        return series

