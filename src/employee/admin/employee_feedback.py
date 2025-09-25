import datetime
from functools import update_wrapper

from dateutil.relativedelta import relativedelta
from django.contrib import admin, messages
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models import Case, Max, OuterRef, Subquery, Value, When
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from config.settings import employee_ids
from employee.forms.employee_feedback import EmployeeFeedbackForm
from employee.models import Employee, EmployeeFeedback
from employee.models.employee_feedback import (
    CommentAgainstEmployeeFeedback,
    EmployeePerformanceFeedback,
)


def get_last_months(start_date):
    for _ in range(3):
        yield start_date.month
        start_date += relativedelta(months=-1)


class CommentAgainstEmployeeFeedbackInline(admin.StackedInline):
    model = CommentAgainstEmployeeFeedback
    extra = 1

    def has_change_permission(self, request, obj=None):
        if obj and (
            request.user.is_superuser
            or request.user.has_perm("employee.can_see_employee_feedback_admin")
        ):
            return True
        return False

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)


@admin.register(EmployeeFeedback)
class EmployeeFeedbackAdmin(admin.ModelAdmin):
    # list_display = ('employee','feedback')
    # #list_editable = ('employee',)
    # list_filter = ('employee', 'rating')
    # search_fields = ('employee__full_name',)
    # autocomplete_fields = ('employee',)

    inlines = (CommentAgainstEmployeeFeedbackInline,)

    def custom_changelist_view(
        self, request, *args, **kwargs
    ) -> TemplateResponse:
        if str(
            request.user.employee.id
        ) not in employee_ids and not request.user.has_perm(
            "employee.can_see_employee_feedback_admin"
        ):
            return redirect("/admin/")

        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        six_months = [i for i in get_last_months(datetime.datetime.today())]

        six_months_names = [months[i - 1] for i in six_months]

        order_keys = {
            "1": "last_feedback_rating",
            "-1": "-last_feedback_rating",
        }

        order_by = ["-current_feedback_exists", "-last_feedback_date"]

        o = request.GET.get("o", None)
        if o and o in order_keys.keys():
            order_by.insert(1, order_keys.get(o))

        e_fback_qs = EmployeeFeedback.objects.filter(
            employee=OuterRef("pk"),
            updated_at__month=timezone.now().date().month,
        )

        employees = (
            Employee.objects.filter(active=True)
            .annotate(
                last_feedback_date=Max("employeefeedback__updated_at"),
                last_feedback_rating=Subquery(
                    e_fback_qs.values("avg_rating")[:1]
                ),
                current_feedback_exists=Case(
                    When(last_feedback_rating=None, then=Value(False)),
                    default=Value(True),
                    output_field=models.BooleanField(),
                ),
            )
            .order_by(*order_by)
        )

        monthly_feedbacks = list()
        for e in employees:
            temp = []
            for month in six_months:
                for fback in e.last_x_months_feedback:
                    if month == fback.created_at.month:
                        temp.append(fback)
                        break
                else:
                    temp.append(None)
            monthly_feedbacks.append(temp)
        context = dict(
            self.admin_site.each_context(request),
            month_names=six_months_names,
            monthly_feedbacks=zip(employees, monthly_feedbacks),
            o=o,  # order key
        )
        return TemplateResponse(
            request,
            "admin/employee_feedback/employee_feedback_admin.html",
            context,
        )

    list_display = (
        "employee",
        "environmental_rating",
        "facilities_rating",
        "learning_growing_rating",
        "avg_rating",
    )
    list_filter = ("employee", "avg_rating")
    search_fields = ("employee__full_name",)
    autocomplete_fields = ("employee",)

    # def get_urls(self):
    #     urls = super(EmployeeFeedbackAdmin, self).get_urls()

    #     employee_online_urls = [
    #         path('my-feedback/', self.employee_feedback_view, name='employee_feedback'),
    #         path('my-feedback-form/', self.employee_feedback_form_view, name='employee_feedback_form'),
    #     ]
    #     return employee_online_urls + urls

    def get_urls(self):
        urls = super(EmployeeFeedbackAdmin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        custome_urls = [
            path(
                "admin/",
                wrap(self.changelist_view),
                name="%s_%s_changelist" % info,
            ),
            path("", self.custom_changelist_view, name="employee_feedback"),
            path(
                "my-feedback/",
                self.employee_feedback_view,
                name="employee_feedback",
            ),
            path(
                "my-feedback-form/",
                self.employee_feedback_form_view,
                name="employee_feedback_form",
            ),
        ]
        return custome_urls + urls

    def employee_feedback_view(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return redirect("/admin/login/")

        if request.method == "GET":
            current_feedback_exists = EmployeeFeedback.objects.filter(
                employee=request.user.employee,
                created_at__gte=datetime.datetime.today().replace(day=1),
            ).exists()
            employee_feedback_objs = EmployeeFeedback.objects.filter(
                employee=request.user.employee
            ).order_by("-created_at")

            form = EmployeeFeedbackForm()

            context = dict(
                self.admin_site.each_context(request),
                employee_feedback_form=form,
                employee_feedback_objs=employee_feedback_objs,
                current_feedback_exists=current_feedback_exists,
            )
            return TemplateResponse(
                request,
                "admin/employee_feedback/employee_feedback.html",
                context,
            )

    def employee_feedback_form_view(self, request, *args, **kwargs):
        employee_feedback_obj = EmployeeFeedback.objects.filter(
            employee=request.user.employee,
            created_at__gte=datetime.datetime.today().replace(day=1),
        ).first()
        if request.method == "POST":
            form = EmployeeFeedbackForm(
                request.POST, instance=employee_feedback_obj
            )
            if form.is_valid():
                form = form.save(commit=False)
                form.employee = request.user.employee
                form.save()
                messages.success(
                    request, "Your feedback has been submitted successfully"
                )
                return redirect("admin:employee_feedback")
            else:
                messages.error(request, "Something went wrong")
                return redirect("admin:employee_feedback")
        elif request.method == "GET":
            form = EmployeeFeedbackForm(instance=employee_feedback_obj)

            context = dict(
                self.admin_site.each_context(request),
                employee_feedback_form=form,
            )

            return TemplateResponse(
                request,
                "admin/employee_feedback/employee_feedback_form_full.html",
                context,
            )

    def get_readonly_fields(self, request, obj):
        if request.user.has_perm("employee.can_see_employee_feedback_admin"):
            return [
                "employee",
                "feedback",
                "avg_rating",
                "environmental_rating",
                "facilities_rating",
                "learning_growing_rating",
                "happiness_index_rating",
                "boss_rating",
            ]
        return []
    
    def has_module_permission(self, request):
        return False

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)

    #     # if request.user.is_superuser and request.user.has_perm('can_see_employee_feedback_admin'):
    #     #     qs = qs.filter(employee = request.user.employee)

    #     return qs


class RatingDefinitionFilter(admin.SimpleListFilter):
    title = _("Rating Definition")
    parameter_name = "rating_definition"

    def lookups(self, request, model_admin):
        return [
            ("exceptional", _("Exceptional")),
            ("exceeds", _("Exceeds")),
            ("meets", _("Meets")),
            ("needs_improvement", _("Needs Improvement")),
            ("unsatisfactory", _("Unsatisfactory")),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        overall_score_expression = (
            models.F("technical_skill") * 0.4
            + models.F("project_deliver") * 0.3
            + models.F("client_feedback") * 0.2
            + models.F("initiative_learning") * 0.1
        )
        queryset = queryset.annotate(
            overall_score_definition=overall_score_expression
        )

        if value == "exceptional":
            return queryset.filter(overall_score_definition__gte=4.5)
        elif value == "exceeds":
            return queryset.filter(
                overall_score_definition__gte=3.5,
                overall_score_definition__lt=4.5,
            )
        elif value == "meets":
            return queryset.filter(
                overall_score_definition__gte=2.5,
                overall_score_definition__lt=3.5,
            )
        elif value == "needs_improvement":
            return queryset.filter(
                overall_score_definition__gte=1.5,
                overall_score_definition__lt=2.5,
            )
        elif value == "unsatisfactory":
            return queryset.filter(overall_score_definition__lt=1.5)
        return queryset


class EligibleForPromotionFilter(admin.SimpleListFilter):
    title = _("Eligible for Promotion")
    parameter_name = "eligible_for_promotion"

    def lookups(self, request, model_admin):
        return [
            ("yes_fast_track", _("Yes (fast-track considered)")),
            ("yes", _("Yes")),
            ("no", _("No")),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        overall_score_expression = (
            models.F("technical_skill") * 0.4
            + models.F("project_deliver") * 0.3
            + models.F("client_feedback") * 0.2
            + models.F("initiative_learning") * 0.1
        )
        queryset = queryset.annotate(
            overall_score_definition=overall_score_expression
        )

        if value == "yes_fast_track":
            return queryset.filter(overall_score_definition__gte=4.5)
        elif value == "yes":
            return queryset.filter(
                overall_score_definition__gte=3.5,
                overall_score_definition__lt=4.5,
            )
        elif value == "no":
            return queryset.filter(overall_score_definition__lt=3.5)
        return queryset


@admin.register(EmployeePerformanceFeedback)
class EmployeePerformanceFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "technical_skill_rating",
        "project_deliver_rating",
        "client_feedback_rating",
        "initiative_learning_rating",
        "rating_definition",
        "total_rating",
        # "boss_rating",
        # "probation_risk",
    )
    list_filter = (
        RatingDefinitionFilter,
        EligibleForPromotionFilter,
        "employee",
    )
    search_fields = ("employee__full_name",)
    autocomplete_fields = ("employee",)

    @admin.display(description="Technical Skill", ordering="technical_skill")
    def technical_skill_rating(self, obj):
        return obj.get_technical_skill_display()

    @admin.display(description="Project Delivery", ordering="project_deliver")
    def project_deliver_rating(self, obj):
        return obj.get_project_deliver_display()

    @admin.display(description="Client Feedback", ordering="client_feedback")
    def client_feedback_rating(self, obj):
        return obj.get_client_feedback_display()

    @admin.display(
        description="Initiative & Learning", ordering="initiative_learning"
    )
    def initiative_learning_rating(self, obj):
        return obj.get_initiative_learning_display()

    @admin.display(description="Rating Definition")
    def rating_definition(self, obj):
        return obj.rating_definition

    @admin.display(description="Total Rating")
    def total_rating(self, obj):
        return obj.overall_score
