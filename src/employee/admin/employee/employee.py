from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.forms import Textarea

from employee.admin.employee._actions import EmployeeActions
from employee.admin.employee.extra_url.index import EmployeeExtraUrls
from employee.admin.employee._inlines import EmployeeInline
from employee.admin.employee._list_view import EmployeeAdminListView
from employee.models import SalaryHistory, Employee, BankAccount, EmployeeSkill
from employee.models.attachment import Attachment
from employee.models.employee import EmployeeLunch, Task, EmployeeNOC


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
    list_filter = ["active", "gender", "permanent_date"]
    autocomplete_fields = ["user", "designation"]
    change_list_template = "admin/employee/list/index.html"
    exclude = ["pf_eligibility"]

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

    def get_list_display(self, request):
        list_display = [
            "employee_info",
            "leave_info",
            "salary_history",
            "skill",
            "tour_allowance",
            "permanent_status",
        ]
        if not request.user.is_superuser:
            list_display.remove("salary_history")
        return list_display

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
        "get_phone",
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


@admin.register(EmployeeNOC)
class EmployeeNOCAdmin(admin.ModelAdmin):
    readonly_fields = ("noc_pdf",)
