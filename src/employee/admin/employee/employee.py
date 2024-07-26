from typing import Any
from django.contrib import admin
from django.db import models
from django import forms
from django.db.models import Q, Sum
from django.forms import Textarea, ValidationError
from datetime import datetime, timedelta

from django.http import HttpRequest
from django.urls import path
from employee.admin.employee._actions import EmployeeActions
from employee.admin.employee.extra_url.index import EmployeeExtraUrls
from employee.admin.employee._inlines import EmployeeInline
from employee.admin.employee._list_view import EmployeeAdminListView
from django.contrib.admin import SimpleListFilter
from employee.models import (
    SalaryHistory,
    Employee,
    BankAccount,
    EmployeeSkill,
    BookConferenceRoom,
)
from config.admin.utils import simple_request_filter
from employee.models.attachment import Attachment
from employee.models.employee import (
    EmployeeLunch,
    EmployeeUnderTPM,
    Task,
    EmployeeNOC,
    Observation,
    LateAttendanceFine,
)
from employee.models.employee_activity import EmployeeProject
from .filter import MonthFilter
from django.utils.html import format_html
from employee.helper.tpm import TPMsBuilder
from employee.helper.tpm import TPMObj


@admin.register(Employee)
class EmployeeAdmin(
    EmployeeAdminListView,
    EmployeeActions,
    EmployeeExtraUrls,
    EmployeeInline,
    admin.ModelAdmin,
):
    search_fields = [
        "full_name",
        "email",
        "salaryhistory__payable_salary",
        "employeeskill__skill__title",
    ]
    list_per_page = 20
    ordering = ["-active"]
    list_filter = ["active", "gender", "permanent_date", "project_eligibility"]
    autocomplete_fields = ["user", "designation"]
    change_list_template = "admin/employee/list/index.html"
    exclude = ["pf_eligibility"]

    def save_model(self, request, obj, form, change):
        print(obj.__dict__)
        if change:
            if (
                obj.lead != form.initial["lead"]
                or obj.manager != form.initial["manager"]
            ):
                # Create an observation record
                already_exist = Observation.objects.filter(employee__id=obj.id).first()
                if not already_exist:
                    Observation.objects.create(
                        employee=obj,
                    )
        super().save_model(request, obj, form, change)
        # Observation.objects.create(
        #             employee_id=obj.id,
        #         )

    def get_readonly_fields(self, request, obj):
        if request.user.is_superuser or request.user.has_perm(
            "employee.can_access_all_employee"
        ):
            return []

        all_fields = [f.name for f in Employee._meta.fields]

        ignore_fields = [
            "id",
            "created_by",
            "created_at",
        ]
        editable_fields = [
            "date_of_birth",
        ]

        for field in editable_fields:
            if field in all_fields:
                all_fields.remove(field)
        for field in ignore_fields:
            if field in all_fields:
                all_fields.remove(field)

        return all_fields

    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super().get_search_results(request, queryset, search_term)

        # Override select2 auto relation to employee
        if request.user.is_authenticated and "autocomplete" in request.get_full_path():
            return (
                Employee.objects.filter(
                    Q(active=True),
                    Q(full_name__icontains=search_term)
                    | Q(email__icontains=search_term),
                ),
                use_distinct,
            )
        return qs, use_distinct

        data = request.GET.dict()

        app_label = data.get("app_label")
        model_name = data.get("model_name")

        # TODO: Fix Permission
        if (
            request.user.is_authenticated
            and app_label == "project_management"
            and model_name == "codereview"
        ):
            qs = Employee.objects.filter(
                active=True, project_eligibility=True, full_name__icontains=search_term
            )
        return qs, use_distinct

    def get_ordering(self, request):
        return ["full_name"]

    def get_list_display(self, request):
        list_display = [
            "employee_info",
            "total_late_attendance_fine",
            "leave_info",
            "salary_history",
            "skill",
            "permanent_status",
        ]
        if not request.user.is_superuser and not request.user.has_perm(
            "employee.can_see_salary_history"
        ):
            list_display.remove("salary_history")
        if not request.user.has_perm("employee.can_access_average_rating"):
            list_display.remove("employee_rating")
        return list_display

    def total_late_attendance_fine(self, obj):
        current_date = datetime.now()
        current_month = current_date.month
        last_month = current_date.month - 1
        last_third_month = current_date.month - 2
        current_year = current_date.year
        current_late_fine = LateAttendanceFine.objects.filter(
            employee=obj, month=current_month, year=current_year
        ).aggregate(fine=Sum("total_late_attendance_fine"))
        last_late_fine = LateAttendanceFine.objects.filter(
            employee=obj, month=last_month, year=current_year
        ).aggregate(fine=Sum("total_late_attendance_fine"))
        third_late_fine = LateAttendanceFine.objects.filter(
            employee=obj, month=last_third_month, year=current_year
        ).aggregate(fine=Sum("total_late_attendance_fine"))
        current_fine = (
            current_late_fine.get("fine", 0.00)
            if current_late_fine.get("fine")
            else 0.00
        )
        last_fine = (
            last_late_fine.get("fine", 0.00) if last_late_fine.get("fine") else 0.00
        )
        third_fine = (
            third_late_fine.get("fine", 0.00) if third_late_fine.get("fine") else 0.00
        )
        last_month_date = current_date + timedelta(days=-30)
        last_third_month_date = current_date + timedelta(days=-60)
        html = f'<b>{third_fine} ({last_third_month_date.strftime("%b, %Y")}) </b><br><b>{last_fine} ({last_month_date.strftime("%b, %Y")}) </b><br><b>{current_fine} ({current_date.strftime("%b, %Y")})</b>'
        return format_html(html)

    total_late_attendance_fine.short_description = "Total Late Fine"

    def get_queryset(self, request):
        if not request.user.is_superuser and not request.user.has_perm(
            "employee.can_access_all_employee"
        ):
            return (
                super(EmployeeAdmin, self)
                .get_queryset(request)
                .filter(user__id=request.user.id)
            )
        return super(EmployeeAdmin, self).get_queryset(request)

    def get_actions(self, request):
        if not request.user.is_superuser:
            return []
        return super(EmployeeAdmin, self).get_actions(request)

    # def get_list_filter(self, request):
    #     if request.user.is_superuser:
    #         return ['active', 'permanent_date']
    #     return []


@admin.register(EmployeeLunch)
class EmployeeDetails(admin.ModelAdmin):
    list_display = (
        "employee",
        "get_designation",
        "get_skill",
        "get_email",
        "get_phone",
        "get_present_address",
        "get_blood_group",
        "get_joining_date_human",
    )
    list_filter = ("active",)
    search_fields = ("employee__full_name", "employee__phone")

    @admin.display(description="Designation", ordering="employee__designation")
    def get_designation(self, obj: EmployeeLunch):
        return obj.employee.designation

    @admin.display(description="Phone")
    def get_phone(self, obj: EmployeeLunch):
        return obj.employee.phone

    @admin.display(description="Email")
    def get_email(self, obj: EmployeeLunch):
        return obj.employee.email

    @admin.display(description="Skill")
    def get_skill(self, obj: EmployeeLunch):
        return obj.employee.top_one_skill

    @admin.display(description="Present Address")
    def get_present_address(self, obj: EmployeeLunch):
        return obj.employee.present_address

    @admin.display(description="Blood Group", ordering="employee__blood_group")
    def get_blood_group(self, obj: EmployeeLunch):
        return obj.employee.blood_group

    @admin.display(description="Job Duration", ordering="employee__joining_date")
    def get_joining_date_human(self, obj: EmployeeLunch):
        return obj.employee.joining_date_human

    def get_queryset(self, request):
        queryset = super(EmployeeDetails, self).get_queryset(request)
        return queryset.filter(employee__active=True)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        elif request.user.employee == obj.employee:
            return ["employee"]
        return ["employee", "active"]


# from employee.models import BookConferenceRoom


class BookConferenceRoomAdmin(admin.ModelAdmin):
    list_display = (
        "manager_or_lead",
        "project_name",
        "start_time",
        "end_time",
        "created_at",
    )
    list_filter = ("manager_or_lead", "project_name", "start_time")
    search_fields = ("manager_or_lead__full_name", "project_name__name")
    ordering = ("start_time",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manager_or_lead":
            kwargs["queryset"] = Employee.objects.filter(Q(manager=True) | Q(lead=True))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(BookConferenceRoom, BookConferenceRoomAdmin)
# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = ['title', 'is_complete', 'note']

#     def get_queryset(self, request):
#         return super().get_queryset(request).filter(created_by=request.user)

from employee.models import EmployeeFAQView, EmployeeFaq


@admin.register(EmployeeFAQView)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "answer"]
    change_list_template = "admin/employee/faq.html"
    search_fields = ["question", "answer"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(active=True).order_by("-rank")

    # def changelist_view(self, request, extra_context):
    # return super().changelist_view(request, extra_context)


@admin.register(EmployeeFaq)
class EmployeeFaqAdmin(admin.ModelAdmin):
    list_display = ["question", "rank", "active"]
    search_fields = ["question", "answer"]
    readonly_fields = ["active"]
    list_filter = ("active",)

    def get_readonly_fields(self, request, obj=None):
        ro_fields = super().get_readonly_fields(request, obj)
        print(ro_fields)

        if request.user.is_superuser or request.user.has_perm(
            "employee.can_approve_faq"
        ):
            ro_fields = filter(lambda x: x not in ["active"], ro_fields)

        return ro_fields

    def has_module_permission(self, request):
        return False


@admin.register(EmployeeNOC)
class EmployeeNOCAdmin(admin.ModelAdmin):
    readonly_fields = ("noc_pdf",)

    def has_module_permission(self, request):
        return False


# @admin.register(Observation)
# class ObservationAdmin(admin.ModelAdmin):
#     list_display = ['employee', 'created_at']  # Add other fields as needed
#     search_fields = ['employee__full_name', 'created_at']  # Add other fields as needed
#     list_filter = ['created_at']  # Add other fields as needed
from django.utils.html import format_html
from calendar import month_name


@admin.register(LateAttendanceFine)
class LateAttendanceFineAdmin(admin.ModelAdmin):
    list_display = ("employee", "get_month_name", "year", "total_late_attendance_fine")
    list_filter = ("employee",)
    date_hierarchy = "date"
    change_list_template = "admin/total_fine.html"

    def get_month_name(self, obj):
        return month_name[obj.month]

    get_month_name.short_description = "Month"

    def get_fields(self, request, obj=None):
        # Specify the fields to be displayed in the admin form, excluding 'month', 'year', and 'date'
        fields = ["employee", "total_late_attendance_fine"]
        return fields

    def get_list_filter(self, request):
        # Customize list_filter to hide the 'month' and 'year' fields for non-superusers
        if request.user.is_superuser or request.user.has_perm(
            "can_view_all_late_attendance"
        ):
            return "employee", "year", "month"
        return ("employee",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "employee.can_view_all_late_attendance"
        ):
            return qs
        return qs.filter(employee=request.user.employee)

    def get_total_fine(self, request):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        if not request.user.is_superuser:
            qs.filter(employee__id__exact=request.user.employee.id)
        return qs.aggregate(total_fine=Sum("total_late_attendance_fine"))

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["total_fine"] = self.get_total_fine(request)["total_fine"]
        return super(self.__class__, self).changelist_view(
            request, extra_context=extra_context
        )


class EmployeeUnderTPMForm(forms.ModelForm):

    class Meta:
        model = EmployeeUnderTPM
        fields = "__all__"
        
    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get("employee")
        tpm = cleaned_data.get("tpm")
        project = cleaned_data.get("project")
        e = EmployeeUnderTPM.objects.filter(employee=employee)
        project_list = e.values_list("project", flat=True)
        if e.exists() and e.first().tpm != tpm:
            raise ValidationError("Employee already under TPM")
        if e.exists() and e.first().tpm == tpm and project in project_list:
            raise ValidationError("Employee already under this TPM with this project")
        return cleaned_data


class TPMFilter(admin.SimpleListFilter):
    title = "TPM"
    parameter_name = "employeeassignedasset__asset__category_id"

    def lookups(self, request, model_admin):
        objs = Employee.objects.filter(is_tpm=True, active=True)
        lookups = [
            (
                ac.id,
                ac.full_name,
            )
            for ac in objs
        ]
        return tuple(lookups)

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            return queryset.filter(tpm__id=value)
        return queryset


@admin.register(EmployeeUnderTPM)
class EmployeeUnderTPMAdmin(admin.ModelAdmin):
    # list_display = ("employee", "tpm", "project")
    list_display = ("tpm", "employee", "project")
    search_fields = ("employee__full_name", "tpm__full_name", "project__title")
    autocomplete_fields = ("employee", "project")
    list_filter = ("tpm", "project", "employee")
    form = EmployeeUnderTPMForm
    change_list_template = "admin/employee/list/tpm_project.html"

    fieldsets = (
        (None, {
            'fields': ('tpm', 'employee', 'project',),
        }),
    )

    def custom_changelist_view(self, request, extra_context=None):
        tpm_project_data = EmployeeUnderTPM.objects.select_related(
            "employee", "project__client", "tpm"
        ).all()
        
        # employees_without_tpm = EmployeeProject.objects.filter(
        #     employee__active=True,
        #     employee__project_eligibility=True
        # ).exclude(
        #     employee_id__in=EmployeeUnderTPM.objects.values('employee_id')
        # )
        employees_without_tpm = Employee.objects.filter(
            active=True,
            project_eligibility=True
        ).exclude(
            id__in=EmployeeUnderTPM.objects.values('employee_id')
        )

        tpm_builder = TPMsBuilder()

        for employee in tpm_project_data:
            tpm_builder.get_or_create(employee)

        other_emp_tpm = Employee(
            full_name="Others"
        )

        for emp_proj in employees_without_tpm:
            for project in emp_proj.employee_projects:
                other_tpm = EmployeeUnderTPM(
                    tpm=other_emp_tpm,
                    employee=emp_proj,
                    project=project
                )
                tpm_builder.get_or_create(other_tpm)

        tpm_builder.update_hours_count()

        my_context = {
            "tpm_project_data": tpm_project_data,
            "tpm_data": tpm_builder.tpm_list,
        }

        return super().changelist_view(request, extra_context=my_context)

    def get_urls(self):
        urls = super(EmployeeUnderTPMAdmin, self).get_urls()
        custom_urls = [
            path("", self.custom_changelist_view, name="tpm_project_changelist_view"),
        ]
        return custom_urls + urls

