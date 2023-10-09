import datetime
from django.contrib import admin, messages
from django.db.models import Q, Sum

from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import format_html, linebreaks, escape
from django.utils.safestring import mark_safe
from django import forms

from employee.admin.employee._forms import DailyUpdateFilterForm

from config.admin import RecentEdit
from config.admin.utils import simple_request_filter
from project_management.models import (
    EmployeeProjectHour,
    DailyProjectUpdate,
    DailyProjectUpdateAttachment,
    DailyProjectUpdateHistory,
)
from project_management.admin.project_hour.options import (
    ProjectManagerFilter,
    ProjectLeadFilter,
)
from project_management.forms import AddDDailyProjectUpdateForm


class ProjectTypeFilter(admin.SimpleListFilter):
    title = "hour type"
    parameter_name = "project_hour__hour_type"

    def lookups(self, request, model_admin):
        return (
            ("project", "Project"),
            ("bonus", "Bonus"),
        )

    def queryset(self, request, queryset):
        if self.value() == "bonus":
            return queryset.filter(
                project_hour__hour_type="bonus",
            )
        elif self.value() == "project":
            return queryset.filter(
                project_hour__hour_type="project",
            )

        return queryset


@admin.register(EmployeeProjectHour)
class EmployeeHourAdmin(RecentEdit, admin.ModelAdmin):
    list_display = (
        "get_date",
        "employee",
        "hours",
        "get_hour_type",
        "project_hour",
    )
    list_filter = (
        ProjectTypeFilter,
        "employee",
        "created_at",
    )
    search_fields = (
        "hours",
        "employee__full_name",
    )
    date_hierarchy = "project_hour__date"
    autocomplete_fields = ("employee", "project_hour")
    change_list_template = "admin/total.html"

    @admin.display(description="Date", ordering="project_hour__date")
    def get_date(self, obj):
        return obj.project_hour.date

    @admin.display(description="Hour Type", ordering="project_hour__hour_type")
    def get_hour_type(self, obj):
        return obj.project_hour.hour_type.title()

    def manager(self, obj):
        return obj.project_hour.manager

    # query for get total hour by query string
    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        if not request.user.is_superuser and not request.user.has_perm(
            "project_management.see_all_employee_hour"
        ):
            if request.user.employee.manager or request.user.employee.lead:
                qs = qs.filter(
                    Q(project_hour__manager=request.user.employee.id)
                    | Q(employee=request.user.employee)
                )
            else:
                qs = qs.filter(employee=request.user.employee)
        return qs.aggregate(tot=Sum("hours"))["tot"]

    # override change list view
    # return total hour count
    def changelist_view(self, request, extra_context=None):
        my_context = {
            "total": self.get_total_hour(request),
        }
        return super(EmployeeHourAdmin, self).changelist_view(
            request, extra_context=my_context
        )

    def get_queryset(self, request):
        """Return query_set

        overrides django admin query set
        allow super admin and permitted user only to see all project hour
        manager's and employees will only see theirs
        @type request: object
        """
        query_set = super(EmployeeHourAdmin, self).get_queryset(request)
        if not request.user.is_superuser and not request.user.has_perm(
            "project_management.see_all_employee_hour"
        ):
            if request.user.employee.manager or request.user.employee.lead:
                return query_set.filter(
                    Q(project_hour__manager=request.user.employee.id)
                    | Q(employee=request.user.employee)
                )
            else:
                return query_set.filter(employee=request.user.employee)
        return query_set

    def get_list_filter(self, request):
        if not request.user.is_superuser and not request.user.has_perm(
            "project_management.see_all_employee_hour"
        ):
            return []
        return super(EmployeeHourAdmin, self).get_list_filter(request)


class DailyProjectUpdateDocumentAdmin(admin.TabularInline):
    model = DailyProjectUpdateAttachment
    extra = 0


@admin.register(DailyProjectUpdate)
class DailyProjectUpdateAdmin(admin.ModelAdmin):
    inlines = [
        DailyProjectUpdateDocumentAdmin,
    ]
    list_display = (
        "get_date",
        "employee",
        "project",
        "get_hours",
        "history",
        "get_update",
        "manager",
        "status_col",
    )
    list_filter = (
        "status",
        "project",
        "employee",
        ProjectManagerFilter,
        ProjectLeadFilter,
    )
    search_fields = (
        "employee__full_name",
        "project__title",
        "manager__full_name",
    )
    date_hierarchy = "created_at"
    autocomplete_fields = (
        "employee",
        "project",
    )
    change_list_template = "admin/total_employee_hour.html"
    readonly_fields = [
        "employee",
        "status",
        "created_at",
        "note",
    ]
    actions = ["update_status_approve", "update_status_pending"]
    form = AddDDailyProjectUpdateForm
    # change_form_template = 'admin/project_management/dailyprojectupdate_form.html'
    # fieldsets = (
    #     (
    #         "Standard Info",
    #         {
    #             "fields": (
    #                 "created_at",
    #                 "employee",
    #                 "manager",
    #                 "project",
    #                 "hours",
    #                 "updates_json",
    #                 "status",
    #             ),
    #         },
    #     ),
    #     (
    #         "Extras",
    #         {
    #             "fields": ("note",),
    #         },
    #     ),
    # )

    class Media:
        css = {"all": ("css/list.css",)}
        js = ("js/list.js", "js/add_daily_update.js")

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return [
                "created_at",
            ]

        if not obj:
            return self.readonly_fields

        if obj:
            # If interact  as selected manager for that project
            if obj.manager == request.user.employee:
                # If interacts also as the employee and manager of that project
                if obj.employee == request.user.employee:
                    return [
                        "created_at",
                    ]

                # If not the employee
                return [
                    "created_at",
                    "employee",
                    "manager",
                    "project",
                    "update",
                ]

            # If interact as the project employee and status approved
            if obj.employee == request.user.employee and obj.status == "approved":
                return self.get_fields(request)

            # If interact as the project employee and status not approved
            return self.readonly_fields

    def history(self, obj):
        historyData = ""
        if obj.history is not None:
            for history in obj.history.order_by("-created_at"):
                historyData += f"{history.hours}"
                if history != obj.history.order_by("-created_at").last():
                    historyData += f" > "
            return format_html(historyData)

        return "No changes"

    @admin.display(description="Date", ordering="created_at")
    def get_date(self, obj):
        return obj.created_at

    @admin.display(description="Update")
    def get_update(self, obj):
        # return obj.update
        html_template = get_template(
            "admin/project_management/list/col_dailyupdate.html"
        )
        html_content = html_template.render(
            {
                "update": obj.update.replace("{", "_").replace("}", "_"),
            }
        )

        try:
            data = format_html(html_content)
        except:
            data = "-"

        return data

    @admin.display(description="Hours", ordering="hours")
    def get_hours(self, obj):
        custom_style = ""
        if obj.hours <= 5:
            custom_style = ' style="color:red; font-weight: bold;"'
        html_content = f"<span{custom_style}>{obj.hours}</span>"
        return format_html(html_content)

    def changelist_view(self, request, extra_context=None):
        filter_form = DailyUpdateFilterForm(
            initial={
                "created_at__date__gte": request.GET.get(
                    "created_at__date__gte",
                    timezone.now().date() - datetime.timedelta(days=7),
                ),
                "created_at__date__lte": request.GET.get(
                    "created_at__date__lte", timezone.now().date()
                ),
            }
        )
        my_context = {
            "total": self.get_total_hour(request),
            "filter_form": filter_form,
        }
        return super(DailyProjectUpdateAdmin, self).changelist_view(
            request, extra_context=my_context
        )

    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        return qs.aggregate(tot=Sum("hours"))["tot"]

    def get_queryset(self, request):
        query_set = super(DailyProjectUpdateAdmin, self).get_queryset(request)

        if not request.user.is_superuser and not request.user.has_perm(
            "project_management.see_all_employee_update"
        ):
            if request.user.employee.manager or request.user.employee.lead:
                query_set = query_set.filter(
                    Q(manager=request.user.employee)
                    | Q(employee=request.user.employee),
                )
            else:
                query_set = query_set.filter(employee=request.user.employee)

        return query_set

    def get_list_filter(self, request):
        filters = list(super(DailyProjectUpdateAdmin, self).get_list_filter(request))
        if not request.user.is_superuser and not request.user.has_perm(
            "project_management.see_all_employee_update"
        ):
            if "employee" in filters:
                filters.remove("employee")
        return filters

    def has_change_permission(self, request, obj=None):
        permitted = super().has_change_permission(request, obj=obj)

        if (
            not request.user.is_superuser
            and obj
            and obj.employee != request.user.employee
            and obj.manager != request.user.employee
        ):
            permitted = False

        return permitted

    @admin.display(description="Status")
    def status_col(self, obj):
        color = "red"
        if obj.status == "approved":
            color = "green"
        return format_html(f'<b style="color: {color}">{obj.get_status_display()}</b>')

    @admin.action(description="Approve selected status daily project updates")
    def update_status_approve(modeladmin, request, queryset):
        if request.user.is_superuser:
            qs_count = queryset.update(status="approved")
        elif request.user.employee.manager or request.user.employee.lead:
            qs_count = queryset.filter(manager_id=request.user.employee.id).update(
                status="approved"
            )

        messages.success(request, f"Marked Approved {qs_count} daily update(s).")

    @admin.action(description="Pending selected status daily project updates")
    def update_status_pending(modeladmin, request, queryset):
        if request.user.is_superuser:
            qs_count = queryset.update(status="pending")
        elif request.user.employee.manager or request.user.employee.lead:
            qs_count = queryset.filter(manager_id=request.user.employee.id).update(
                status="pending"
            )
            queryset = queryset.filter(manager_id=request.user.employee.id)

        messages.success(request, f"Marked Pending {qs_count} daily update(s).")

    def has_delete_permission(self, request, obj=None):
        permitted = super().has_delete_permission(request, obj=obj)
        if (
            not request.user.is_superuser
            and obj
            and obj.employee != request.user.employee
        ):
            permitted = False
        return permitted

    def save_model(self, request, obj, form, change) -> None:
        if not obj.employee_id:
            obj.employee_id = request.user.employee.id

        print('#########\n\n',form.cleaned_data)

        super().save_model(request, obj, form, change)

        if change == False:
            return DailyProjectUpdateHistory.objects.create(
                hours=request.POST.get("hours"), daily_update=obj
            )

        requested_hours = float(request.POST.get("hours"))
        if requested_hours != obj.hours or obj.created_by is not request.user:
            return DailyProjectUpdateHistory.objects.create(
                hours=request.POST.get("hours"), daily_update=obj
            )

    # def add_view(self, request, form_url='', extra_context=None):
    #     print('Inside form update view..')
    #     # Customize the form instance
    #     self.form = AddDDailyProjectUpdateForm
    #     extra_context = {'form':self.form}
    #     return super().add_view(request, form_url, extra_context)
