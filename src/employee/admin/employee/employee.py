from django.contrib import admin

from django import forms
from django.db.models import Q, Sum
from django.forms import ValidationError
from datetime import datetime, timedelta


from django.urls import path

from employee.admin.employee._actions import EmployeeActions
from employee.admin.employee.extra_url.index import EmployeeExtraUrls
from employee.admin.employee._inlines import EmployeeInline
from employee.admin.employee._list_view import EmployeeAdminListView

from employee.admin.employee.filter import TopSkillFilter
from employee.models.bank_account import BEFTN
from employee.tasks import new_late_attendance_calculate
from project_management.models import EmployeeProjectHour, Project
from user_auth.models import UserLogs
from django.utils import timezone
from employee.models import (
    Employee,
    BookConferenceRoom,
)
from config.admin.utils import simple_request_filter

from employee.models.employee import (
    EmployeeLunch,
    EmployeeUnderTPM,
    Inbox,
    LessHour,
    EmployeeNOC,
    MeetingSummary,
    Observation,
    LateAttendanceFine,
    TPMComplain,
)
from django.template.loader import get_template

from django.utils.html import format_html, strip_tags
from employee.helper.tpm import TPMsBuilder


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
    list_filter = [
        "active",
        "gender",
        "permanent_date",
        "project_eligibility",
        TopSkillFilter,
    ]
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
            "get_attachment",
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
        # if not request.user.has_perm("employee.can_access_average_rating"):
        #     list_display.remove("employee_rating")
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
                .select_related(
                    "user",
                    "designation",
                    "leave_management",
                    "pay_scale",
                )
            )
        return (
            super(EmployeeAdmin, self)
            .get_queryset(request)
            .select_related(
                "user",
                "designation",
                "leave_management",
                "pay_scale",
            )
        )

    def get_actions(self, request):
        actions = super(EmployeeAdmin, self).get_actions(request)

        if request.user.is_superuser:
            return actions

        # Define permission-based allowed actions
        permission_action_map = {
            "employee.can_print_salary_certificate": [
                "print_salary_certificate",
                "print_salary_certificate_all_months",
            ],
            "employee.can_print_salary_payslip": ["print_salary_pay_slip_all_months"],
            "employee.can_send_mail_to_employee": [
                "mail_appointment_letter",
                "mail_permanent_letter",
                "mail_increment_letter",
                "mail_noc_letter",
            ],
            "employee.can_print_employee_info": [
                "generate_noc_letter",
                "print_appointment_letter",
                "print_permanent_letter",
                "print_increment_letter",
                "print_noc_letter",
                "print_resignation_letter",
                "print_tax_salary_certificate",
                "print_bank_forwarding_letter",
                "print_promotion_letter",
                "print_experience_letter",
                "download_employee_info",
            ],
        }

        allowed_actions = []

        # Check permissions and collect allowed actions
        for perm, action_list in permission_action_map.items():
            if request.user.has_perm(perm):
                allowed_actions.extend(action_list)

        # If there are allowed actions, filter the actions
        if allowed_actions:
            actions = {
                name: action
                for name, action in actions.items()
                if name in allowed_actions
            }
            return actions

        return {}


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
    list_display = (
        "date",
        "get_employee",
        "get_month_name",
        "get_year",
        "total_late_attendance_fine",
        "entry_time",
    )
    list_filter = ("employee", "is_consider")
    date_hierarchy = "date"
    autocomplete_fields = ("employee",)
    change_list_template = "admin/total_fine.html"

    @admin.display(description="Employee", ordering="employee__full_name")
    def get_employee(self, obj):
        consider_count = LateAttendanceFine.objects.filter(
            date__month=obj.date.month, date__year=obj.date.year, is_consider=True
        ).count()
        if consider_count > 0:
            return f"{obj.employee} ({consider_count})"
        return obj.employee

    # get_employee.short_description = "Employee"

    def get_month_name(self, obj):
        return month_name[obj.date.month]

    get_month_name.short_description = "Month"

    def get_year(self, obj):
        return obj.date.year

    get_year.short_description = "Year"

    def get_fields(self, request, obj=None):
        # Specify the fields to be displayed in the admin form, excluding 'month', 'year', and 'date'
        fields = ["employee", "total_late_attendance_fine", "date", "is_consider"]
        return fields

    # def get_list_filter(self, request):
    #     # Customize list_filter to hide the 'month' and 'year' fields for non-superusers
    #     if request.user.is_superuser or request.user.has_perm(
    #         "can_view_all_late_attendance"
    #     ):
    #         return ("employee",)
    #     return ("employee",)

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

    def save_model(self, request, obj, form, change):
        if not obj.year:
            obj.year = obj.date.year
        if not obj.month:
            obj.month = obj.date.month
        obj.save()


class EmployeeUnderTPMForm(forms.ModelForm):
    class Meta:
        model = EmployeeUnderTPM
        fields = "__all__"
        # widgets = {
        #     "employee": forms.Select(
        #         attrs={"class": "form-control", "required": False}
        #     ),
        # }

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
        (
            None,
            {
                "fields": (
                    "tpm",
                    "employee",
                    "project",
                ),
            },
        ),
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
        employee_id_with_tpm = tpm_project_data.filter(
            employee__isnull=False
        ).values_list("employee_id", flat=True)
        employees_without_tpm = Employee.objects.filter(
            active=True,
            project_eligibility=True,
            is_tpm=False,
        ).exclude(id__in=employee_id_with_tpm)

        tpm_builder = TPMsBuilder()

        for employee in tpm_project_data:
            tpm_obj = tpm_builder.get_or_create(employee)
            tpm_obj.add_project_hours()
        other_emp_tpm = Employee(full_name="Others")
        other_project_id = set()
        for emp_proj in employees_without_tpm:
            for project in emp_proj.employee_projects:
                other_project_id.add(project.id)
                other_tpm = EmployeeUnderTPM(
                    tpm=other_emp_tpm, employee=emp_proj, project=project
                )
                tpm_obj = tpm_builder.get_or_create(other_tpm)
                tpm_obj.add_project_hours()

        tpm_dev_project_ids = list(
            tpm_project_data.values_list("project_id", flat=True)
        ) + list(other_project_id)

        active_project_without_dev = Project.objects.filter(active=True).exclude(
            id__in=list(set(tpm_dev_project_ids))
        )

        for project in active_project_without_dev:
            other_tpm = EmployeeUnderTPM(
                tpm=other_emp_tpm, employee=other_emp_tpm, project=project
            )
            tpm_obj = tpm_builder.get_or_create(other_tpm)
            tpm_obj.add_project_hours()

        tpm_builder.update_hours_count()

        total_expected, total_actual = tpm_builder.get_total_expected_and_got_hour_tpm()
        formatted_weekly_sums = tpm_builder.get_formatted_weekly_sums()

        my_context = {
            "tpm_project_data": tpm_project_data,
            "tpm_data": tpm_builder.tpm_list,
            "total_expected": total_expected,
            "total_actual": total_actual,
            "formatted_weekly_sums": formatted_weekly_sums,
        }

        return super().changelist_view(request, extra_context=my_context)

    def get_urls(self):
        urls = super(EmployeeUnderTPMAdmin, self).get_urls()
        custom_urls = [
            path("", self.custom_changelist_view, name="tpm_project_changelist_view"),
        ]
        return custom_urls + urls


@admin.register(TPMComplain)
class TPMComplainAdmin(admin.ModelAdmin):
    list_filter = ("tpm", "status", "employee")
    list_display = (
        "employee",
        "tpm",
        "short_complain",
        "short_management_feedback",
        "status_colored",
    )
    autocomplete_fields = ("employee",)
    readonly_fields = ()

    def get_fields(self, request, obj=None):
        # Show the 'tpm' field only if the user is a superuser
        fields = [
            "employee",
            "project",
            "complain_title",
            "complain",
            "feedback_title",
            "management_feedback",
            "status",
        ]
        if request.user.is_superuser:
            fields.insert(0, "tpm")  # Insert 'tpm' at the beginning
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.employee.is_tpm:
            return qs.filter(tpm=request.user.employee).select_related(
                "employee", "tpm"
            )
        return qs.select_related("employee", "tpm")

    def employee(self, obj):
        return obj.employee.full_name or "-"

    def tpm(self, obj):
        return obj.tpm.full_name or "-"

    def get_readonly_fields(self, request, obj=None):
        if request.user.employee.is_tpm:
            return self.readonly_fields + (
                "management_feedback",
                "status",
                "feedback_title",
            )
        return self.readonly_fields

    def status_colored(self, obj):
        if obj.status == "pending":
            color = "red"
        elif obj.status == "approved":
            color = "green"
        elif obj.status == "observation":
            color = "blue"
        else:
            color = "black"  # Default color

        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_colored.short_description = "Status"

    def short_complain(self, obj):
        return self._truncate_text_with_tooltip(strip_tags(obj.complain))

    def short_management_feedback(self, obj):
        return self._truncate_text_with_tooltip(strip_tags(obj.management_feedback))

    def _truncate_text_with_tooltip(self, text, length=100):
        if text:
            if len(text) > length:
                truncated_text = text[:length] + "..."
            else:
                truncated_text = text
            return format_html(
                '<span title="{}">{}</span>',
                text,  # Full text for tooltip
                truncated_text,  # Shortened text for display
            )

    short_complain.short_description = "Complain"
    short_management_feedback.short_description = "Management Feedback"

    def save_model(self, request, obj, form, change):
        if request.user.employee.is_tpm:
            obj.tpm = request.user.employee
        super().save_model(request, obj, form, change)


from django.contrib.sessions.models import Session
from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from django.db.models import Q


class ActiveUserOnlyFilter(RelatedOnlyFieldListFilter):
    def field_choices(self, field, request, model_admin):
        # Fetch users with first_name and last_name
        users = field.related_model.objects.filter(is_active=True).distinct()

        # Generate choices based on first_name and last_name
        choices = [(user.id, f"{user.first_name} {user.last_name}") for user in users]

        return choices


class ActiveUserFilter(admin.SimpleListFilter):
    title = "currently logged in"
    parameter_name = "currently_logged_in"

    def lookups(self, request, model_admin):
        return (
            ("Active", "Active"),
            ("Inactive", "Inactive"),
        )

    def queryset(self, request, queryset):
        if self.value() == "Active":
            active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            active_user_ids = [
                session.get_decoded().get("_auth_user_id")
                for session in active_sessions
            ]
            return queryset.filter(user__id__in=active_user_ids)
        elif self.value() == "Inactive":
            active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            active_user_ids = [
                session.get_decoded().get("_auth_user_id")
                for session in active_sessions
            ]
            return queryset.exclude(user__id__in=active_user_ids)
        return queryset


@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = (
        "user_info",
        "location",
        "device_name",
        "operating_system",
        "browser_name",
        "ip_address",
        "loging_time",
    )
    search_fields = ("name", "email", "designation")
    list_filter = (ActiveUserFilter, "loging_time", ("user", ActiveUserOnlyFilter))
    ordering = ("-loging_time",)
    actions = ["logout_selected_users", "logout_all_users"]

    def user_info(self, obj):
        user = obj.user
        # Safely format the HTML with format_html and remove boldness from email and designation
        return format_html(
            "{} {}<br>"
            '<span style="font-weight: normal;">{}</span><br>'
            '<span style="font-weight: normal;">{}</span>',
            user.first_name,
            user.last_name,
            user.email,
            getattr(user.employee.designation, "title", "Not Available"),
        )

    user_info.short_description = "User Info"

    @staticmethod
    def logout_user(queryset):
        for log in queryset:
            # Get all sessions
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            for session in sessions:
                data = session.get_decoded()
                if data.get("_auth_user_id") == str(log.id):
                    session.delete()  # Log out the user by deleting the session

    def logout_selected_users(self, request, queryset):
        self.logout_user(queryset)
        self.message_user(request, f"Selected users have been logged out.")

    logout_selected_users.short_description = "Logout selected users"

    def logout_all_users(self, request, queryset):
        from django.contrib.auth.models import User

        # here i want to set custom queryset
        custom_queryset = User.objects.filter(is_active=True)
        self.logout_user(custom_queryset)
        self.message_user(request, f"All users have been logged out.")

    logout_all_users.short_description = "Logout all users"


@admin.register(BEFTN)
class BEFTNAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Sender Information",
            {
                "fields": (
                    "originating_bank_account_number",
                    "originating_bank_routing_number",
                    "originating_bank_account_name",
                ),
            },
        ),
        (
            "Receiver Information",
            {
                "fields": ("routing_no",),
            },
        ),
    )

    list_display = ("originating_bank_account_name",)


class LessHourForm(forms.ModelForm):
    class Meta:
        model = LessHour
        fields = "__all__"

    def clean(self):
        data = super().clean()
        date = data.get("date")
        if timezone.now().date() < date:
            raise forms.ValidationError("You can't select future date")
        if date.weekday() != 4:
            raise forms.ValidationError("Today is not Friday")
        return data


@admin.register(LessHour)
class LessHourAdmin(admin.ModelAdmin):
    list_display = ("date", "employee", "get_skill", "tpm", "get_hour", "get_feedback")
    date_hierarchy = "date"
    list_filter = ("tpm", "employee")
    # fields = ["employee", "tpm", "date"]
    exclude = ("tpm",)
    autocomplete_fields = ("employee",)
    form = LessHourForm

    class Media:
        css = {"all": ("css/list.css",)}

    @admin.display(description="Hour")
    def get_hour(self, obj):
        employee_expected_hours = (
            obj.employee.monthly_expected_hours / 4
            if obj.employee.monthly_expected_hours
            else 0
        )
        employee_hours = (
            EmployeeProjectHour.objects.filter(
                project_hour__tpm=obj.tpm,
                project_hour__date=obj.date,
                project_hour__hour_type="project",
                employee=obj.employee,
            )
            .aggregate(total_hours=Sum("hours"))
            .get("total_hours", 0)
            or 0
        )
        return f"{int(employee_expected_hours)} ({int(employee_hours)})"

    @admin.display(description="Skill", ordering="employee__top_one_skill")
    def get_skill(self, obj):
        return obj.employee.top_one_skill

    @admin.display(description="Feedback", ordering="feedback")
    def get_feedback(self, obj):
        # return obj.update
        html_template = get_template("admin/employee/list/col_less_hour_feedback.html")

        is_github_link_show = True
        html_content = html_template.render(
            {
                "feedback": obj.feedback if obj.feedback else "-",
                "is_github_link_show": is_github_link_show,
            }
        )

        try:
            data = format_html(html_content)
        except:
            data = "-"

        return data

    def save_form(self, request, form, change):
        obj = super().save_form(request, form, change)
        employee_tpm = EmployeeUnderTPM.objects.filter(employee=obj.employee)
        tpm = employee_tpm.first().tpm if employee_tpm.exists() else None
        obj.tpm = tpm
        obj.save()
        return obj

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields = list(fields)
        if not obj and not request.user.is_superuser:
            fields.remove("feedback")
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.employee.is_tpm:
            return qs.filter(tpm=request.user.employee)
        return qs


class MeetingSummaryInline(admin.TabularInline):
    model = MeetingSummary
    extra = 1
    readonly_fields = ("created_by",)


class InboxReadStatusFilter(admin.SimpleListFilter):
    title = "Read Status"
    parameter_name = "is_read"

    def lookups(self, request, model_admin):
        return (
            ("read", "Read"),
            ("unread", "Unread"),
        )

    def queryset(self, request, queryset):
        if self.value() == "read":
            return queryset.filter(is_read=True)
        if self.value() == "unread":
            return queryset.filter(is_read=False)


@admin.register(Inbox)
class InboxAdmin(admin.ModelAdmin):
    list_display = (
        "get_date",
        "employee",
        "get_summary",
        "get_discuss_with",
        "get_read_status",
    )
    list_filter = ("employee", InboxReadStatusFilter)
    # search_fields = ("sender__full_name", "receiver__full_name")
    autocomplete_fields = ("employee",)
    inlines = (MeetingSummaryInline,)
    change_list_template = "admin/employee/change_list.html"
    change_form_template = "admin/employee/change_view.html"
    exclude = ("is_read",)

    class Media:
        css = {"all": ("css/list.css",)}
        # js = ("employee/js/inbox.js",)

    @admin.display(description="Date")
    def get_date(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")

    @admin.display(description="Read Status")
    def get_read_status(self, obj):
        return "Read" if obj.is_read else "Unread"

    @admin.display(description="Summary")
    def get_summary(self, obj):
        summaries = obj.meeting_summary_inbox.all()
        html_template = get_template("admin/employee/list/col_summary.html")
        html_content = html_template.render(
            {"summaries": summaries, "summary": summaries.first()}
        )
        return format_html(html_content)

    @admin.display(description="Discuss with")
    def get_discuss_with(self, obj):
        return obj.created_by.employee.full_name

    def get_queryset(self, request):
        if not request.user.has_perm("employee.can_see_all_employee_inbox"):
            return super().get_queryset(request).filter(employee=request.user.employee)
        return super().get_queryset(request)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if request.method == "GET":
            obj = self.get_object(request, object_id)
            obj.is_read = True
            obj.save()
        return super().change_view(request, object_id, form_url, extra_context)
