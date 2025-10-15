from datetime import datetime, timedelta

from django import forms
from django.contrib import admin
from django.db.models import Q, Sum
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.template.loader import get_template
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe

from config.admin.utils import simple_request_filter
from employee.admin.employee._actions import EmployeeActions
from employee.admin.employee._inlines import EmployeeInline
from employee.admin.employee._list_view import EmployeeAdminListView
from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery
from employee.admin.employee.extra_url.index import EmployeeExtraUrls
from employee.admin.employee.filter import TopSkillFilter
from employee.helper.tpm import TPMsBuilder
from employee.models import (
    BookConferenceRoom,
    Employee,
)
from employee.models.attachment import EmployeeTaxAcknowledgement

# from employee.models.bank_account import BEFTN
from employee.models.employee import (
    EmployeeAvailableSlot,
    EmployeeFAQView,
    EmployeeLunch,
    EmployeeNOC,
    EmployeeUnderTPM,
    # Inbox,
    LateAttendanceFine,
    # LessHour,
    # MeetingSummary,
    Observation,
    # TPMComplain,
    # generate_employee_profile_pdf,
)
from employee.models.employee_activity import (
    EmployeeAttendance,
    EmployeeProject,
)
from employee.models.employee_skill import EmployeeSkill
from employee.models.employee_social import SocialMedia
from project_management.models import EmployeeProjectHour, Project
from settings.models import FinancialYear
from user_auth.models import UserLogs


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


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

    # Add all fields from the Employee model
    fields = [
        "active",
        "user",
        "email",
        "blood_group",
        "tax_info",
        "image",
        "gender",
        "date_of_birth",
        "address",
        "present_address",
        "phone",
        "joining_date",
        "national_id_no",
        "permanent_date",
        "designation",
        "leave_management",
        "pay_scale",
        "is_tpm",
        "tax_eligible",
        "manager",
        "lead",
        "sqa",
        "exception_la",
        # "show_in_web",
        "operation",
        "lunch_allowance",
        "project_eligibility",
        "leave_in_cash_eligibility",
        "show_in_attendance_list",
        "festival_bonus_eligibility",
        # "device_allowance",
        # "list_order",
        # "birthday_image",
        # "birthday_image_shown",
        # "need_cto",
        # "need_cto_at",
        # "need_hr",
        # "need_hr_at",
        "entry_pass_id",
        "monthly_expected_hours",
    ]

    def lookup_allowed(self, lookup, value):
        if lookup in ["employeeskill__skill__title__exact"]:
            return True
        return super().lookup_allowed(lookup, value)

    # def save_model(self, request, obj, form, change):
    #     print(obj.__dict__)
    #     if change:
    #         if (
    #             obj.lead != form.initial["lead"]
    #             or obj.manager != form.initial["manager"]
    #         ):
    #             # Create an observation record
    #             already_exist = Observation.objects.filter(
    #                 employee__id=obj.id
    #             ).first()
    #             if not already_exist:
    #                 Observation.objects.create(
    #                     employee=obj,
    #                 )
    #     super().save_model(request, obj, form, change)
    #     # Observation.objects.create(
    #     #             employee_id=obj.id,
    #     #         )

    def save_model(self, request, obj, form, change):
        # Your existing logic
        if change:
            if (
                obj.lead != form.initial["lead"]
                or obj.manager != form.initial["manager"]
            ):
                already_exist = Observation.objects.filter(
                    employee__id=obj.id
                ).first()
                if not already_exist:
                    Observation.objects.create(
                        employee=obj,
                    )

        # Save the object first
        super().save_model(request, obj, form, change)

        # Generate and save PDF
        # try:
        #     pdf_content = generate_employee_profile_pdf(obj)
        #     pdf_filename = f"{obj.full_name}_profile_{obj.id}.pdf".replace(" ", "_")
        #     obj.profile_pdf.save(pdf_filename, pdf_content, save=True)
        #     # Verify the file was saved
        #     if obj.profile_pdf and obj.profile_pdf.name:
        #         print(f"PDF saved successfully for {obj.full_name}: {obj.profile_pdf.name}")
        #     else:
        #         print(f"Failed to save PDF for {obj.full_name}: No file associated")
        # except Exception as e:
        #     # Log detailed error for debugging
        #     import traceback
        #     print(f"Error generating/saving PDF for {obj.full_name}: {e}")
        #     print(traceback.format_exc())

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
        query_params = request.GET
        qs, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        # Override select2 auto relation to employee
        if (
            query_params.get("model_name")
            and query_params.get("model_name") == "tdschallan"
        ):
            return (
                Employee.objects.filter(
                    Q(full_name__icontains=search_term)
                    | Q(email__icontains=search_term),
                ),
                use_distinct,
            )
        if (
            request.user.is_authenticated
            and "autocomplete" in request.get_full_path()
        ):
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
                active=True,
                project_eligibility=True,
                full_name__icontains=search_term,
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
            last_late_fine.get("fine", 0.00)
            if last_late_fine.get("fine")
            else 0.00
        )
        third_fine = (
            third_late_fine.get("fine", 0.00)
            if third_late_fine.get("fine")
            else 0.00
        )
        last_month_date = current_date + timedelta(days=-30)
        last_third_month_date = current_date + timedelta(days=-60)
        html = f"<b>{third_fine} ({last_third_month_date.strftime('%b, %Y')}) </b><br><b>{last_fine} ({last_month_date.strftime('%b, %Y')}) </b><br><b>{current_fine} ({current_date.strftime('%b, %Y')})</b>"
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
            "employee.can_print_salary_payslip": [
                "print_salary_pay_slip_all_months"
            ],
            "employee.can_send_mail_to_employee": [
                "mail_appointment_letter",
                "mail_permanent_letter",
                "mail_increment_letter",
                "mail_noc_letter",
                "mail_role_change_letter",
                "mail_promotion_letter",
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
                "download_employee_details",
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
        # "get_skill",
        "social_links",
        "get_email",
        "get_phone",
        # "get_present_address",
        "get_blood_group",
        "get_joining_date_human",
    )
    list_filter = ("active",)
    search_fields = ("employee__full_name", "employee__phone")

    from django.utils.safestring import mark_safe

    # @admin.display(description="Social Links")
    # def social_links(self, obj: EmployeeLunch):
    #     employee = obj.employee
    #     socials = employee.employeesocial_set.all()

    #     if not socials:
    #         return "— NO SOCIALS —"

    #     links = []
    #     for es in socials:
    #         platform = "personal"
    #         if es.social_name and es.social_name.title:
    #             platform = es.social_name.title.lower()
    #         elif es.title:
    #             platform = es.title.lower()
    #         links.append(f"{platform}: {es.url}")

    #     return " | ".join(links)
    @admin.display(
        description="Social Links", ordering="employee__employeesocial"
    )
    def social_links(self, obj: EmployeeLunch):
        employee = obj.employee
        socials = employee.employeesocial_set.all()

        if not socials:
            return "—"

        icons_html = []

        # Inline SVG icons — no external CSS or JS needed
        platform_config = {
            "linkedin": {
                "svg": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#0A66C2"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
            },
            "facebook": {
                "svg": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
            },
            "github": {
                "svg": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#333"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>',
            },
            "twitter": {
                "svg": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#1DA1F2"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723 10.054 10.054 0 01-3.127 1.195 4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.937 4.937 0 004.604 3.417 9.868 9.868 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.054 0 14-7.496 14-13.986 0-.209 0-.42-.015-.63a9.936 9.936 0 002.46-2.548l-.047-.02z"/></svg>',
            },
            "instagram": {
                "svg": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#E1306C"><path d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.259 0 3.665.016 4.948.071 1.277.06 2.148.261 2.913.558.788.306 1.459.717 2.126 1.384.666.666 1.079 1.336 1.384 2.126.296.766.499 1.636.558 2.913.06 1.28.072 1.686.072 4.947s-.015 3.667-.072 4.947c-.06 1.277-.261 2.148-.558 2.913-.306.788-.717 1.459-1.384 2.126-.667.666-1.336 1.079-2.126 1.384-.766.296-1.636.499-2.913.558-1.28.06-1.687.072-4.947.072-3.259 0-3.665-.015-4.947-.071-1.277-.06-2.148-.261-2.913-.558-.788-.306-1.459-.717-2.126-1.384-.666-.666-1.079-1.336-1.384-2.126-.296-.766-.499-1.636-.558-2.913-.06-1.28-.072-1.686-.072-4.947s.015-3.667.072-4.947c.06-1.277.261-2.149.558-2.913.306-.789.717-1.459 1.384-2.126.666-.667 1.336-1.079 2.126-1.384.766-.296 1.636-.499 2.913-.558 1.28-.06 1.687-.071 4.947-.071zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.162 6.162 6.162 6.162-2.759 6.162-6.162-2.759-6.162-6.162-6.162zM12 16c-2.206 0-4-1.794-4-4s1.794-4 4-4 4 1.794 4 4-1.794 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"/></svg>',
            },
            "personal": {
                "svg": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#555"><path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8z"/><path d="M13 16h-2v-4h2v4zm0-6h-2V8h2v2z"/></svg>',
            },
        }

        for es in socials:
            platform = "personal"
            if es.social_name and es.social_name.title:
                platform = es.social_name.title.lower().strip()
            elif es.title:
                platform = es.title.lower().strip()

            config = platform_config.get(platform, platform_config["personal"])
            svg_icon = config["svg"]

            # Wrap SVG in clickable link
            link_html = format_html(
                '<a href="{}" target="_blank" title="{}" style="margin-right: 12px; display: inline-block; text-decoration: none;">{}</a>',
                es.url,
                platform.capitalize(),
                mark_safe(svg_icon),
            )
            icons_html.append(link_html)

        return mark_safe("".join(icons_html))

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

    @admin.display(
        description="Job Duration", ordering="employee__joining_date"
    )
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

    def has_module_permission(self, request):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manager_or_lead":
            kwargs["queryset"] = Employee.objects.filter(
                Q(manager=True) | Q(lead=True)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(BookConferenceRoom, BookConferenceRoomAdmin)
# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = ['title', 'is_complete', 'note']

#     def get_queryset(self, request):
#         return super().get_queryset(request).filter(created_by=request.user)

from employee.models import EmployeeFaq


@admin.register(EmployeeFAQView)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "answer"]
    change_list_template = "admin/employee/faq.html"
    search_fields = ["question", "answer"]

    def get_queryset(self, request):
        return (
            super().get_queryset(request).filter(active=True).order_by("-rank")
        )
        
    def has_module_permission(self, request):
        return False

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
from calendar import month_name


@admin.register(LateAttendanceFine)
class LateAttendanceFineAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "get_employee",
        "get_month_name",
        "get_year",
        # "total_late_attendance_fine",
        "entry_time",
    )
    list_filter = ("employee", "is_consider")
    date_hierarchy = "date"
    autocomplete_fields = ("employee",)
    change_list_template = "admin/total_fine.html"
    actions = ["create_late_fines_for_current_month"]

    def create_late_fines_for_current_month(self, request, queryset=None):
        """
        Create LateAttendanceFine records for employees who have late entries
        in the current month but don't already have a fine record.
        First sends an email with the list of late attendance details.
        No selection of items from the admin table is required.
        """
        now = datetime.now()
        current_month = now.month
        current_year = now.year

        # Get all attendance records for current month
        attendances = EmployeeAttendance.objects.filter(
            date__year=current_year,
            date__month=current_month,
            entry_time__isnull=False,
            employee__active=True,
            employee__show_in_attendance_list=True,
            employee__exception_la=False,
        ).select_related("employee")

        # Dictionary to store late attendance details per employee
        late_attendance_details = {}

        for att in attendances:
            entry_time = att.entry_time
            hour = entry_time.hour
            minute = entry_time.minute
            employee_is_lead = att.employee.lead or att.employee.manager

            # Determine if attendance is late (using 10-minute rule for all dates)
            is_late = (
                employee_is_lead
                and ((hour == 11 and minute > 10) or hour >= 12)
            ) or (
                not employee_is_lead
                and ((hour >= 11 and minute > 10) or hour >= 12)
            )

            if is_late:
                employee_id = att.employee.id
                if employee_id not in late_attendance_details:
                    late_attendance_details[employee_id] = {
                        "name": att.employee.full_name,
                        "email": att.employee.email,
                        "phone": att.employee.phone,
                        "dates": [],
                        "entry_times": [],
                        "total_late_days": 0,
                        "employee": att.employee,
                    }

                late_attendance_details[employee_id]["dates"].append(
                    att.date.strftime("%Y-%m-%d")
                )
                late_attendance_details[employee_id]["entry_times"].append(
                    entry_time.strftime("%H:%M")
                )
                late_attendance_details[employee_id]["total_late_days"] += 1

        # Create LateAttendanceFine records for each unique late date
        created_fines = []
        for employee_id, details in late_attendance_details.items():
            for late_date, entry_time in zip(
                details["dates"], details["entry_times"]
            ):
                # Check if a fine already exists for this employee and specific date
                existing_fine = LateAttendanceFine.objects.filter(
                    employee=details["employee"],  # Use 'employee' key
                    month=current_month,
                    year=current_year,
                    date=late_date,
                ).exists()

                if not existing_fine:
                    # Create a new LateAttendanceFine record for this date
                    fine = LateAttendanceFine(
                        employee=details["employee"],
                        month=current_month,
                        year=current_year,
                        total_late_attendance_fine=0.00,  # Ignored as per request
                        date=late_date,
                        is_consider=True,
                        entry_time=entry_time,
                    )
                    fine.save()
                    created_fines.append(fine)

        # Provide feedback to the user
        if created_fines:
            self.message_user(
                request,
                f"Created {len(created_fines)} new LateAttendanceFine records.",
            )
        else:
            self.message_user(
                request, "No new LateAttendanceFine records were created."
            )

        # Redirect back to the changelist view to avoid resubmission
        return HttpResponseRedirect(request.get_full_path())

    create_late_fines_for_current_month.short_description = (
        "Create late fines for current month"
    )

    @admin.display(description="Employee", ordering="employee__full_name")
    def get_employee(self, obj):
        consider_count = LateAttendanceFine.objects.filter(
            date__month=obj.date.month,
            date__year=obj.date.year,
            is_consider=True,
        ).count()
        if consider_count > 0:
            return f"{obj.employee} ({consider_count})"
        return obj.employee

    def get_month_name(self, obj):
        return month_name[obj.date.month]

    get_month_name.short_description = "Month"

    def get_year(self, obj):
        return obj.date.year

    get_year.short_description = "Year"

    def get_fields(self, request, obj=None):
        fields = [
            "employee",
            "total_late_attendance_fine",
            "date",
            "is_consider",
        ]
        return fields

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

    def get_total_late_entries(self, request):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        if not request.user.is_superuser:
            try:
                qs = qs.filter(employee__id__exact=request.user.employee.id)
            except AttributeError:
                return 0
        return qs.count()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["total_late_entries"] = self.get_total_late_entries(
            request
        )
        extra_context["total_fine"] = self.get_total_fine(request)["total_fine"]
        return super(self.__class__, self).changelist_view(
            request, extra_context=extra_context
        )
        # return super().changelist_view(request, extra_context=extra_context)

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
            raise ValidationError(
                "Employee already under this TPM with this project"
            )
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


from django.db.models import (
    BooleanField,
    Case,
    Count,
    F,
    Max,
    Min,
    OuterRef,
    Prefetch,
    Subquery,
    Value,
    When,
)

from config.settings import employee_ids as management_ids


@admin.register(EmployeeUnderTPM)
class EmployeeUnderTPMAdmin(admin.ModelAdmin):
    # list_display = ("employee", "tpm", "project")
    list_display = ("tpm", "employee", "project")
    search_fields = ("employee__full_name", "tpm__full_name", "project__title")
    autocomplete_fields = ("employee", "project")
    list_filter = ("tpm", "project", "employee")
    form = EmployeeUnderTPMForm
    change_list_template = "admin/employee/list/tpm_project.html"
    list_per_page = 50

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
        other_emp_project = Project(title="Others")
        other_project_id = set()
        for emp_proj in employees_without_tpm:
            if not emp_proj.employee_projects:
                other_tpm = EmployeeUnderTPM(
                    tpm=other_emp_tpm,
                    employee=emp_proj,
                    project=other_emp_project,
                )
                tpm_obj = tpm_builder.get_or_create(other_tpm)
                tpm_obj.add_project_hours()
            else:
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

        active_project_without_dev = Project.objects.filter(
            active=True
        ).exclude(id__in=list(set(tpm_dev_project_ids)))

        for project in active_project_without_dev:
            other_tpm = EmployeeUnderTPM(
                tpm=other_emp_tpm, employee=other_emp_tpm, project=project
            )
            tpm_obj = tpm_builder.get_or_create(other_tpm)
            tpm_obj.add_project_hours()

        tpm_builder.update_hours_count()

        total_expected, total_actual = (
            tpm_builder.get_total_expected_and_got_hour_tpm()
        )
        formatted_weekly_sums = tpm_builder.get_formatted_weekly_sums()
        employee = request.user.employee
        employee_filter = Q(employee__active=True) & Q(
            employee__project_eligibility=True
        )
        if not employee.operation and not employee.is_tpm:
            employee_filter &= Q(employee=employee)
        best_skill_qs = (
            EmployeeSkill.objects.filter(employee_id=OuterRef("employee_id"))
            .order_by("-percentage")
            .values("skill__title")[:1]
        )
        employee_projects = (
            EmployeeProject.objects.filter(employee_filter)
            .exclude(employee_id__in=management_ids)
            .annotate(
                project_count=Count("project"),
                project_order=Min("project"),
                project_exists=Case(
                    When(project_count=0, then=Value(False)),
                    default=Value(True),
                    output_field=BooleanField(),
                ),
                is_online=F("employee__employeeonline__active"),
                employee_skill=Subquery(best_skill_qs),
            )
            .order_by(
                "project_exists",
                "employee__full_name",
            )
            .select_related(
                "employee",
            )
            .prefetch_related(
                Prefetch(
                    "employee__employeeskill_set",
                    queryset=EmployeeSkill.objects.order_by("-percentage"),
                ),
                Prefetch("employee__employeeskill_set__skill"),
                Prefetch(
                    "project",
                    queryset=Project.objects.filter(active=True),
                ),
            )
        )

        order_keys = {
            "1": "employee__full_name",
            "-1": "-employee__full_name",
            "2": "project_order",
            "-2": "-project_order",
        }

        order_by = request.GET.get("ord", None)
        if order_by:
            order_by_list = ["project_exists", order_keys.get(order_by, "1")]
            if order_by not in ["1", "-1"]:
                order_by_list.append("employee__full_name")

            employee_projects = employee_projects.order_by(*order_by_list)
        employee_formal_summery = EmployeeNearbySummery()
        permanents, permanents_count = employee_formal_summery.permanents()
        my_context = {
            "tpm_project_data": tpm_project_data,
            "tpm_data": tpm_builder.tpm_list,
            "total_expected": total_expected,
            "total_actual": total_actual,
            "formatted_weekly_sums": formatted_weekly_sums,
            "employee_projects": employee_projects,
            "ord": order_by,
            "increments": employee_formal_summery.increments,
            "permanents": permanents,
            "permanents_count": permanents_count,
        }

        return super().changelist_view(request, extra_context=my_context)

    def get_urls(self):
        urls = super(EmployeeUnderTPMAdmin, self).get_urls()
        custom_urls = [
            path(
                "",
                self.custom_changelist_view,
                name="tpm_project_changelist_view",
            ),
        ]
        return custom_urls + urls

    class Media:
        js = ("employee/js/hide_employee_under_tpm_changelist.js",)


# @admin.register(TPMComplain)
# class TPMComplainAdmin(admin.ModelAdmin):
#     list_filter = ("tpm", "status", "employee")
#     list_display = (
#         "employee",
#         "tpm",
#         "short_complain",
#         "short_management_feedback",
#         "status_colored",
#     )
#     autocomplete_fields = ("employee",)
#     readonly_fields = ()

#     def get_fields(self, request, obj=None):
#         # Show the 'tpm' field only if the user is a superuser
#         fields = [
#             "employee",
#             "project",
#             "complain_title",
#             "complain",
#             "feedback_title",
#             "management_feedback",
#             "status",
#         ]
#         if request.user.is_superuser:
#             fields.insert(0, "tpm")  # Insert 'tpm' at the beginning
#         return fields

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.employee.is_tpm:
#             return qs.filter(tpm=request.user.employee).select_related(
#                 "employee", "tpm"
#             )
#         return qs.select_related("employee", "tpm")

#     def employee(self, obj):
#         return obj.employee.full_name or "-"

#     def tpm(self, obj):
#         return obj.tpm.full_name or "-"

#     def get_readonly_fields(self, request, obj=None):
#         if request.user.employee.is_tpm:
#             return self.readonly_fields + (
#                 "management_feedback",
#                 "status",
#                 "feedback_title",
#             )
#         return self.readonly_fields

#     def status_colored(self, obj):
#         if obj.status == "pending":
#             color = "red"
#         elif obj.status == "approved":
#             color = "green"
#         elif obj.status == "observation":
#             color = "blue"
#         else:
#             color = "black"  # Default color

#         return format_html(
#             '<span style="color: {};">{}</span>',
#             color,
#             obj.get_status_display(),
#         )

#     status_colored.short_description = "Status"

#     def short_complain(self, obj):
#         return self._truncate_text_with_tooltip(strip_tags(obj.complain))

#     def short_management_feedback(self, obj):
#         return self._truncate_text_with_tooltip(
#             strip_tags(obj.management_feedback)
#         )

#     def _truncate_text_with_tooltip(self, text, length=100):
#         if text:
#             if len(text) > length:
#                 truncated_text = text[:length] + "..."
#             else:
#                 truncated_text = text
#             return format_html(
#                 '<span title="{}">{}</span>',
#                 text,  # Full text for tooltip
#                 truncated_text,  # Shortened text for display
#             )

#     short_complain.short_description = "Complain"
#     short_management_feedback.short_description = "Management Feedback"

#     def save_model(self, request, obj, form, change):
#         if request.user.employee.is_tpm:
#             obj.tpm = request.user.employee
#         super().save_model(request, obj, form, change)


from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from django.contrib.sessions.models import Session


class ActiveUserOnlyFilter(RelatedOnlyFieldListFilter):
    def field_choices(self, field, request, model_admin):
        # Fetch users with first_name and last_name
        users = field.related_model.objects.filter(is_active=True).distinct()

        # Generate choices based on first_name and last_name
        choices = [
            (user.id, f"{user.first_name} {user.last_name}") for user in users
        ]

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
            active_sessions = Session.objects.filter(
                expire_date__gte=timezone.now()
            )
            active_user_ids = [
                session.get_decoded().get("_auth_user_id")
                for session in active_sessions
            ]
            return queryset.filter(user__id__in=active_user_ids)
        elif self.value() == "Inactive":
            active_sessions = Session.objects.filter(
                expire_date__gte=timezone.now()
            )
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
    list_filter = (
        ActiveUserFilter,
        "loging_time",
        ("user", ActiveUserOnlyFilter),
    )
    ordering = ("-loging_time",)
    actions = ["logout_selected_users", "logout_all_users"]
    
    def has_module_permission(self, request):
        return False

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
        self.message_user(request, "Selected users have been logged out.")

    logout_selected_users.short_description = "Logout selected users"

    def logout_all_users(self, request, queryset):
        from django.contrib.auth.models import User

        # here i want to set custom queryset
        custom_queryset = User.objects.filter(is_active=True)
        self.logout_user(custom_queryset)
        self.message_user(request, "All users have been logged out.")

    logout_all_users.short_description = "Logout all users"


# @admin.register(BEFTN)
# class BEFTNAdmin(admin.ModelAdmin):
#     fieldsets = (
#         (
#             "Sender Information",
#             {
#                 "fields": (
#                     "originating_bank_account_number",
#                     "originating_bank_routing_number",
#                     "originating_bank_account_name",
#                 ),
#             },
#         ),
#         (
#             "Receiver Information",
#             {
#                 "fields": ("routing_no",),
#             },
#         ),
#     )

#     list_display = ("originating_bank_account_name",)


# class LessHourForm(forms.ModelForm):
#     class Meta:
#         model = LessHour
#         fields = "__all__"

#     def clean(self):
#         data = super().clean()
#         date = data.get("date")
#         if timezone.now().date() < date:
#             raise forms.ValidationError("You can't select future date")
#         if date.weekday() != 4:
#             raise forms.ValidationError("Today is not Friday")
#         return data


# @admin.register(LessHour)
# class LessHourAdmin(admin.ModelAdmin):
#     list_display = (
#         "date",
#         "employee",
#         "get_skill",
#         "tpm",
#         "get_hour",
#         "get_feedback",
#     )
#     date_hierarchy = "date"
#     list_filter = ("tpm", "employee")
#     # fields = ["employee", "tpm", "date"]
#     exclude = ("tpm",)
#     autocomplete_fields = ("employee",)
#     form = LessHourForm

#     class Media:
#         css = {"all": ("css/list.css",)}

#     @admin.display(description="Hour")
#     def get_hour(self, obj):
#         employee_expected_hours = (
#             obj.employee.monthly_expected_hours / 4
#             if obj.employee.monthly_expected_hours
#             else 0
#         )
#         employee_hours = (
#             EmployeeProjectHour.objects.filter(
#                 # project_hour__tpm=obj.tpm,
#                 project_hour__date=obj.date,
#                 project_hour__hour_type="project",
#                 employee=obj.employee,
#             )
#             .aggregate(total_hours=Sum("hours"))
#             .get("total_hours", 0)
#             or 0
#         )
#         return f"{int(employee_expected_hours)} ({int(employee_hours)})"

#     @admin.display(description="Skill", ordering="employee__top_one_skill")
#     def get_skill(self, obj):
#         return obj.employee.top_one_skill

#     @admin.display(description="Feedback", ordering="feedback")
#     def get_feedback(self, obj):
#         # return obj.update
#         html_template = get_template(
#             "admin/employee/list/col_less_hour_feedback.html"
#         )

#         is_github_link_show = True
#         html_content = html_template.render(
#             {
#                 "feedback": obj.feedback if obj.feedback else "-",
#                 "is_github_link_show": is_github_link_show,
#             }
#         )

#         try:
#             data = format_html(html_content)
#         except:
#             data = "-"

#         return data

#     def save_form(self, request, form, change):
#         obj = super().save_form(request, form, change)
#         employee_tpm = EmployeeUnderTPM.objects.filter(employee=obj.employee)
#         tpm = employee_tpm.first().tpm if employee_tpm.exists() else None
#         obj.tpm = tpm
#         obj.save()
#         return obj

#     def get_fields(self, request, obj=None):
#         fields = super().get_fields(request, obj)
#         fields = list(fields)
#         if not obj and not request.user.is_superuser:
#             fields.remove("feedback")

#         if not request.user.is_superuser and not request.user.has_perm(
#             "employee.can_see_hr_feedback_field"
#         ):
#             fields.remove("hr_feedback")
#         return fields

#     def get_readonly_fields(self, request, obj=None):
#         fields = super().get_readonly_fields(request, obj)
#         fields = list(fields)
#         if not request.user.is_superuser and not request.user.has_perm(
#             "employee.can_see_hr_feedback_field"
#         ):
#             fields.append("hr_feedback")

#         return fields

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.employee.is_tpm:
#             return qs.filter(tpm=request.user.employee)
#         return qs


# class MeetingSummaryInline(admin.TabularInline):
#     model = MeetingSummary
#     extra = 1
#     readonly_fields = ("created_by",)


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


# @admin.register(Inbox)
# class InboxAdmin(admin.ModelAdmin):
#     list_display = (
#         "get_date",
#         "employee",
#         "get_summary",
#         "get_discuss_with",
#         "get_read_status",
#     )
#     list_filter = ("employee", InboxReadStatusFilter)
#     # search_fields = ("sender__full_name", "receiver__full_name")
#     autocomplete_fields = ("employee",)
#     inlines = (MeetingSummaryInline,)
#     change_list_template = "admin/employee/change_list.html"
#     change_form_template = "admin/employee/change_view.html"
#     exclude = ("is_read",)

#     class Media:
#         css = {"all": ("css/list.css",)}
#         # js = ("employee/js/inbox.js",)

#     @admin.display(description="Date")
#     def get_date(self, obj):
#         return obj.created_at.strftime("%Y-%m-%d")

#     @admin.display(description="Read Status")
#     def get_read_status(self, obj):
#         return "Read" if obj.is_read else "Unread"

#     @admin.display(description="Summary")
#     def get_summary(self, obj):
#         summaries = obj.meeting_summary_inbox.all()
#         html_template = get_template("admin/employee/list/col_summary.html")
#         html_content = html_template.render(
#             {"summaries": summaries, "summary": summaries.first()}
#         )
#         return format_html(html_content)

#     @admin.display(description="Discuss with")
#     def get_discuss_with(self, obj):
#         return obj.created_by.employee.full_name

#     def get_queryset(self, request):
#         if not request.user.has_perm("employee.can_see_all_employee_inbox"):
#             return (
#                 super()
#                 .get_queryset(request)
#                 .filter(employee=request.user.employee)
#             )
#         return super().get_queryset(request)

#     def change_view(self, request, object_id, form_url="", extra_context=None):
#         if request.method == "GET":
#             obj = self.get_object(request, object_id)
#             obj.is_read = True
#             obj.save()
#         return super().change_view(request, object_id, form_url, extra_context)


def last_four_financial_year(index=0):
    last_four_year_financial_year = FinancialYear.objects.all().order_by("-id")[
        :4
    ]
    try:
        return last_four_year_financial_year[index]
    except IndexError:
        return "-"


from django.contrib import admin


@admin.register(EmployeeTaxAcknowledgement)
class EmployeeTaxAcknowledgementAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "first_year",
        "second_year",
        "third_year",
        "fourth_year",
    )
    list_filter = ("tds_year", "employee")
    autocomplete_fields = ("employee",)

    def _file_link(self, attachment):
        if not attachment:
            return "-"
        text = "📄"
        return format_html(
            '<a href="{}" target="_blank">{}</a>', attachment.file.url, text
        )

    def get_queryset(self, request):
        latest_ids = (
            EmployeeTaxAcknowledgement.objects.values("employee")
            .annotate(max_id=Max("id"))  # latest id
            .values_list("max_id", flat=True)  # [123, 456, …]
        )

        qs = EmployeeTaxAcknowledgement.objects.filter(
            id__in=list(latest_ids)
        ).select_related("employee", "tds_year")

        if not request.user.has_perm("employee.view_all_tax_acknowledgement"):
            qs = qs.filter(employee=request.user.employee)

        return qs

    def _year_column(self, obj, offset):
        fy = last_four_financial_year(offset)
        if isinstance(fy, str):
            return "-"
        att = (
            EmployeeTaxAcknowledgement.objects.filter(
                employee=obj.employee, tds_year=fy
            )
            .select_related("tds_year", "employee")
            .first()
        )
        return self._file_link(att)

    def first_year(self, obj):
        return self._year_column(obj, offset=0)

    def second_year(self, obj):
        return self._year_column(obj, 1)

    def third_year(self, obj):
        return self._year_column(obj, 2)

    def fourth_year(self, obj):
        return self._year_column(obj, 3)

    def _header(self, offset):
        fy = last_four_financial_year(offset)
        return str(fy) if not isinstance(fy, str) else f"Year-{offset + 1}"

    first_year.short_description = last_four_financial_year(0)
    second_year.short_description = last_four_financial_year(1)
    third_year.short_description = last_four_financial_year(2)
    fourth_year.short_description = last_four_financial_year(3)


from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

# class TodayFirstEmployeeFilter(SimpleListFilter):
#     title = _("employee")
#     parameter_name = "employee"
#     template = "admin/employee/list/avail_slot_filter.html"

#     def lookups(self, request, model_admin):
#         today = timezone.now().date()

#         # employees with an AVAILABLE slot today
#         today_pks = set(
#             EmployeeAvailableSlot.objects.filter(
#                 date__date=today, available=True
#             ).values_list("employee", flat=True)
#         )

#         # build choices: red-labelled today guys first
#         choices = []
#         for emp in Employee.objects.filter(pk__in=today_pks).order_by("full_name"):
#             choices.append(
#                 (emp.pk, format_html('<span style="color:red;font-weight:bold">{}</span>', emp))
#             )

#         # everybody else, alphabetical
#         for emp in Employee.objects.exclude(pk__in=today_pks).filter(active=True).order_by("full_name"):
#             choices.append((emp.pk, str(emp)))

#         return choices

#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(employee__id=self.value())
#         return queryset


# class TodayFirstEmployeeFilter(SimpleListFilter):
#     title = _("employee")
#     parameter_name = "employee"
#     template = "admin/employee/list/avail_slot_filter.html"

#     def lookups(self, request, model_admin):
#         today = timezone.now().date()

#         # Employees with an AVAILABLE slot today
#         today_pks = set(
#             EmployeeAvailableSlot.objects.filter(
#                 date__date=today, available=True
#             ).values_list("employee", flat=True)
#         )

#         # Build choices: prioritize today’s available employees, style based on slot
#         choices = []
#         for emp in Employee.objects.filter(pk__in=today_pks).order_by("full_name"):
#             # Get the latest slot for the employee
#             latest_slot = EmployeeAvailableSlot.objects.filter(employee=emp).order_by("-date").first()
#             slot_value = latest_slot.slot if latest_slot else None
#             label = (
#                 format_html('<span style="color:red;font-weight:bold">{}</span>', emp)
#                 if slot_value == "full"
#                 else str(emp)
#             )
#             choices.append((emp.pk, label))

#         # Other active employees
#         for emp in Employee.objects.exclude(pk__in=today_pks).filter(active=True).order_by("full_name"):
#             latest_slot = EmployeeAvailableSlot.objects.filter(employee=emp).order_by("-date").first()
#             slot_value = latest_slot.slot if latest_slot else None
#             label = (
#                 format_html('<span style="color:red;font-weight:bold">{}</span>', emp)
#                 if slot_value == "full"
#                 else str(emp)
#             )
#             choices.append((emp.pk, label))

#         return choices

#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(employee__id=self.value())
#         return queryset


class TodayFirstEmployeeFilter(SimpleListFilter):
    title = _("employee")
    parameter_name = "employee"
    template = "admin/employee/list/avail_slot_filter.html"

    def lookups(self, request, model_admin):
        today = timezone.now().date()

        # Employees with an AVAILABLE slot today
        today_pks = set(
            EmployeeAvailableSlot.objects.filter(
                date__date=today, available=True
            ).values_list("employee", flat=True)
        )

        # Build choices: prioritize today’s available employees, style based on slot
        choices = []
        for emp in Employee.objects.filter(pk__in=today_pks).order_by(
            "full_name"
        ):
            # Get the latest slot for the employee
            latest_slot = (
                EmployeeAvailableSlot.objects.filter(employee=emp)
                .order_by("-date")
                .first()
            )
            slot_value = latest_slot.slot if latest_slot else None
            label = (
                format_html(
                    '<span style="color:red;font-weight:bold">{}</span>', emp
                )
                if slot_value in ["full", "half"]
                else str(emp)
            )
            choices.append((emp.pk, label))

        # Other active employees
        for emp in (
            Employee.objects.exclude(pk__in=today_pks)
            .filter(active=True)
            .order_by("full_name")
        ):
            latest_slot = (
                EmployeeAvailableSlot.objects.filter(employee=emp)
                .order_by("-date")
                .first()
            )
            slot_value = latest_slot.slot if latest_slot else None
            label = (
                format_html(
                    '<span style="color:red;font-weight:bold">{}</span>', emp
                )
                if slot_value in ["full", "half"]
                else str(emp)
            )
            choices.append((emp.pk, label))

        return choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(employee__id=self.value())
        return queryset


@admin.register(EmployeeAvailableSlot)
class EmployeeAvailableSlotAdmin(admin.ModelAdmin):
    list_display = ("date_display", "employee", "available", "slot")
    list_filter = ("available", "slot", TodayFirstEmployeeFilter)
    autocomplete_fields = ("employee",)
    date_hierarchy = "date"

    def date_display(self, obj):
        return obj.date.strftime("%d %b %Y – %I:%M %p")

    date_display.short_description = "Date & Time"
    date_display.admin_order_field = "date"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
