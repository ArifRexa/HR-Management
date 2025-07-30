from datetime import datetime, timedelta
from distutils.util import strtobool

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.auth import hashers
from django.contrib.auth.models import User
from django.core import management
from django.db.models import Count, Prefetch, Q, QuerySet
from django.shortcuts import redirect
from django.template.loader import get_template, render_to_string
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.utils.html import format_html, linebreaks
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task, schedule

from config import settings
from job_board.mails.mail import re_apply_alert_mail
from job_board.management.commands.send_offer_letter import generate_attachment
from job_board.models import SMSPromotion
from job_board.models.candidate import (
    Candidate,
    CandidateApplicationSummary,
    CandidateAssessment,
    CandidateAssessmentReview,
    CandidateJob,
    Feedback,
    JobPreferenceRequest,
    ResetPassword,
)
from job_board.models.candidate_email import CandidateEmail, CandidateEmailAttatchment
from job_board.models.job import Job

# from job_board.views.apis.authentication import ApplicationSummaryView


class CandidateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(), strip=False, required=False
    )

    class Meta:
        model = Candidate
        fields = "__all__"


class HasFeedbackFilter(SimpleListFilter):
    title = _("Feedback")
    parameter_name = "feedback"

    def lookups(self, request, model_admin):
        return [
            ("yes", _("Yes")),
            ("no", _("No")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            # Filter candidates who have feedback
            return queryset.filter(feedbacks__isnull=False).distinct()
        elif self.value() == "no":
            # Filter candidates who do not have feedback
            return queryset.filter(feedbacks__isnull=True).distinct()
        return queryset


class ScheduleDateFilter(admin.SimpleListFilter):
    title = _("Schedule Date")
    parameter_name = "schedule_date"

    def lookups(self, request, model_admin):
        # Get distinct dates and count candidates for each schedule date
        # queryset = Candidate.objects.exclude(schedule_datetime__date=None).values('schedule_datetime__date').annotate(
        #     candidate_count=Count('schedule_datetime')
        # ).order_by('schedule_datetime__date')

        past_seven_days = timezone.now().date() - timedelta(days=7)

        queryset = (
            Candidate.objects.filter(
                schedule_datetime__date__gte=past_seven_days,
                schedule_datetime__date__isnull=False,
            )
            .values("schedule_datetime__date")
            .annotate(candidate_count=Count("schedule_datetime"))
            .order_by("schedule_datetime__date")
        )

        # Return list of schedule dates with counts
        # return [
        #     (str(entry['schedule_datetime__date']), f"{entry['schedule_datetime__date']} ({entry['candidate_count']})")
        #     for entry in queryset
        # ]
        today_date = timezone.now().date()
        return [
            (
                str(entry["schedule_datetime__date"]),
                (
                    "Today"
                    if entry["schedule_datetime__date"] == today_date
                    else DateFormat(entry["schedule_datetime__date"]).format("d M y")
                    + f" ({entry['candidate_count']})"
                ),
            )
            for entry in queryset
        ]

    def queryset(self, request, queryset):
        if self.value():
            # Filter by the selected date
            return queryset.filter(schedule_datetime__date=self.value())
        return queryset


class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 1
    fields = ("comment", "created_at")  # Remove 'user' from fields
    readonly_fields = ("created_at",)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "user":
            kwargs["initial"] = request.user
            kwargs["queryset"] = User.objects.filter(
                is_staff=True
            )  # Limit to staff users
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deletion in the inline


# from django.core.paginator import Paginator
# class DumbPaginator(Paginator):
#     @cached_property
#     def count(self):
#         return 10**9


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    change_form_template = "admin/candidate/custom_candidate_form.html"
    search_fields = ("full_name", "email", "phone")
    # list_display = ('contact_information', 'assessment', 'note', 'review', 'expected_salary')
    list_filter = (
        "candidatejob__job",
        "gender",
        "is_shortlisted",
        "is_called",
        "application_status",
        HasFeedbackFilter,
        ScheduleDateFilter,
    )
    actions = (
        "send_default_sms",
        "send_offer_letter",
        "download_offer_letter",
        "job_re_apply",
    )
    date_hierarchy = "created_at"
    inlines = [FeedbackInline]
    exclude = ("feedback",)

    list_per_page = 30

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Prefetch jobs ordered by newest first
        qs = qs.prefetch_related(
            Prefetch(
                "candidatejob_set",
                queryset=CandidateJob.objects.order_by("-id").prefetch_related(
                    Prefetch(
                        "candidate_assessment",
                        queryset=CandidateAssessment.objects.select_related(
                            "assessment"
                        ).prefetch_related("candidateassessmentreview_set"),
                        to_attr="assessments",
                    )
                ),
                to_attr="jobs",
            ),
            Prefetch(
                "feedbacks",
                queryset=Feedback.objects.select_related("user__employee"),
                to_attr="cached_feedbacks",
            ),
        )
        return qs

    class Media:
        css = {
            "all": (
                "css/list.css",
                "https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css",
                "https://cdn.jsdelivr.net/npm/flatpickr/dist/plugins/confirmDate/confirmDate.css",
            )
        }
        js = (
            "https://cdn.jsdelivr.net/npm/flatpickr",
            "https://cdn.jsdelivr.net/npm/flatpickr/dist/plugins/confirmDate/confirmDate.js",
            "js/candidate_actions.js",
        )

    def get_list_display(self, request):
        if request.user.is_superuser or request.user.has_perm(
            "job_board.can_see_candidate_expected_salary"
        ):
            return (
                "contact_information",
                "assessment",
                "candidate_actions",
                "review",
                "note",
                "expected_salary",
            )
        else:
            return (
                "contact_information",
                "assessment",
                "candidate_actions",
                "review",
                "note",
            )

    @admin.display(description="Actions")
    def candidate_actions(self, obj):
        template = "admin/candidate/list/col_actions.html"
        context = {
            "candidate": obj,
            "id": obj.id,
        }
        return format_html(render_to_string(template, context))

    @admin.display(ordering="candidatejob__expected_salary")
    def expected_salary(self, obj: Candidate):
        jobs = getattr(obj, "jobs", None)
        candidate_job = jobs[-1] if jobs else None
        if candidate_job is not None:
            return candidate_job.expected_salary

    @admin.display(ordering="created_at")
    def contact_information(self, obj: Candidate):
        jobs = getattr(obj, "jobs", None)
        candidate_job = jobs[-1] if jobs else None
        return format_html(
            f"{obj.full_name} <br>"
            f"{obj.email} <br>"
            f"{obj.phone} <br>"
            f'{candidate_job.created_at.strftime("%b. %d-%Y") if candidate_job else ""}<br><br>'
            f'<a href="{obj.cv.url}" target="blank">Resume</a>'
        )

    @admin.display(ordering="created_at")
    def assessment(self, obj):
        job = obj.jobs[0] if hasattr(obj, "jobs") and obj.jobs else None
        if job:
            assessments = job.assessments  # already prefetched CandidateAssessment
            html = get_template("admin/candidate/list/col_assessment.html").render(
                {
                    "candidate_job": job,
                    "candidate_assessments": assessments,
                }
            )
            return html
        return "-"

    from django.utils.html import format_html

    def review(self, obj: Candidate):
        feedbacks = getattr(obj, "cached_feedbacks", None)
        if not feedbacks:
            return ""

        # Create truncated feedback
        truncated_feedback_list = ""
        full_feedback_list = ""

        for feedback in feedbacks:
            # Truncate feedback text to 50 characters, add '...'
            truncated_comment = (
                (feedback.comment[:30] + "...")
                if len(feedback.comment) > 50
                else feedback.comment
            )
            truncated_feedback_list += f"<p><strong>{feedback.user.employee.full_name}:</strong> {truncated_comment}</p>"

            # Full feedback (for hover), preserving line breaks
            # Use string concatenation to handle the line breaks
            full_feedback_list += (
                "<p><strong>{}<br>---------------------</strong><br>{}</p>".format(
                    feedback.user, feedback.comment.replace("\n", "<br>")
                )
            )

        # Render truncated feedback in the list, but show full feedback on hover
        return format_html(
            f'<div class="feedback-wrapper">'
            f'    <span class="feedback-hover">{truncated_feedback_list}</span>'
            f'    <div class="feedback-popup">{full_feedback_list}</div>'
            f"</div>"
        )

    @admin.display()
    def note(self, obj: Candidate):
        jobs = getattr(obj, "jobs", None)
        candidate_job = jobs[-1] if jobs else None
        if candidate_job:
            return format_html(
                linebreaks(
                    candidate_job.additional_message.replace("{", "_").replace("}", "_")
                    if candidate_job.additional_message is not None
                    else None
                )
            )

    @admin.display(description="Send Default Promotional SMS")
    def send_default_sms(self, request, queryset):
        promotion = SMSPromotion.objects.filter(is_default=True).first()
        if promotion:
            for candidate in queryset:
                async_task(
                    "job_board.tasks.employee_sms_promotion",
                    promotion.sms_body,
                    candidate,
                    group=f"{candidate.full_name} Got an Promotional SMS",
                )

    @admin.action(description="Send Offer letter (Email)")
    def send_offer_letter(self, request, queryset):
        for candidate in queryset:
            management.call_command("send_offer_letter", candidate.pk)

    @admin.action(description="Download Offer Letter (PDF)")
    def download_offer_letter(self, request, queryset):
        for candidate in queryset:
            return generate_attachment(candidate).render_to_pdf()

    @admin.action(description="Job Application Re-Apply alert")
    def job_re_apply(self, request, queryset):
        for candidate in queryset:
            re_apply_alert_mail(candidate)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        candidate_jobs_qs = (
            CandidateJob.objects.filter(candidate_id=object_id)
            .order_by("-id")
            .select_related("job")
            .prefetch_related(
                Prefetch(
                    "candidate_assessment",
                    queryset=CandidateAssessment.objects.select_related(
                        "assessment"
                    ).prefetch_related("candidateassessmentreview_set"),
                    to_attr="assessments",
                )
            )
        )
        extra_context["candidate_jobs"] = list(candidate_jobs_qs)
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def save_model(self, request, obj, form, change):
        try:
            super(CandidateAdmin, self).save_model(request, obj, form, change)
        except Exception:
            obj.password = hashers.make_password(
                request.POST["password"], settings.CANDIDATE_PASSWORD_HASH
            )
            super(CandidateAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete()

        # Save or update remaining instances
        for instance in instances:
            if not instance.user_id:
                instance.user = request.user
            instance.save()

        formset.save_m2m()


@admin.register(CandidateJob)
class CandidateJobAdmin(admin.ModelAdmin):
    list_display = (
        "candidate",
        "get_job",
        "expected_salary",
        "get_assessment",
        "meta_information",
        "merit",
    )
    list_display_links = ("get_job", "candidate")
    search_fields = ("candidate__full_name", "candidate__email", "candidate__phone")
    list_filter = ("merit", "job", "candidate_assessment__assessment")
    list_per_page = 20
    ordering = ("pk",)

    @admin.display(description="Job", ordering="job")
    def get_job(self, obj):
        return obj.job.title

    @admin.display(description="Assessment", ordering="job__assessment")
    def get_assessment(self, obj: CandidateJob):
        assessment_result = ""
        for ddd in obj.candidate_assessment.all():
            assessment_result += f"{ddd.assessment} {ddd.result} {ddd.score} <br>"
        return format_html(assessment_result)

    @admin.display(description="additional_message")
    def meta_information(self, obj: CandidateJob):
        return format_html(obj.additional_message.replace("\n", "<br>"))

    def has_module_permission(self, request):
        return False


@admin.register(CandidateApplicationSummary)
class CandidateApplicationSummaryAdmin(admin.ModelAdmin):
    change_list_template = (
        "admin/application_summary.html"  # Custom template for the change list
    )
    list_display = ("job", "year", "month", "application_count")
    list_filter = ("job", "year", "month")
    actions = ["generate_summary"]

    # Define custom URLs
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "summary/",
                self.admin_site.admin_view(self.application_summary_view),
                name="application_summary",
            ),
        ]
        return custom_urls + urls

    # Automatically redirect to application_summary
    def changelist_view(self, request, extra_context=None):
        return redirect("admin:application_summary")

    def application_summary_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            "title": "Hiring Opportunities to Previous Candidates",
            "jobs": Job.objects.all(),
            "years": range(datetime.now().year, datetime.now().year - 4, -1),
        }
        return TemplateResponse(request, "admin/application_summary.html", context)

    # Action to generate the summary
    def generate_summary(self, request, queryset):
        CandidateApplicationSummary.generate_summary()
        self.message_user(request, "Application summary has been generated.")

    generate_summary.short_description = "Generate application summary"


class CandidateHasUrlFilter(SimpleListFilter):
    title = "Has Evaluation Url"
    parameter_name = "evaluation_url__isnull"

    def lookups(self, request, model_admin):
        return (
            (False, "Has Link"),
            (True, "Has not Link"),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            to_bol = bool(strtobool(self.value()))
            dd = queryset.filter(evaluation_url__isnull=to_bol)
            return dd


class CandidateHasMetaReviewFilter(SimpleListFilter):
    title = "Has Meta Review"
    parameter_name = "meta_review__isnull"

    def lookups(self, request, model_admin):
        return (
            (False, "Has No Meta Review"),
            (True, "Has Meta Review"),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            has_meta_review_value = bool(strtobool(self.value()))
            if not has_meta_review_value:
                queryset = queryset.filter(
                    Q(note__isnull=True) | Q(note=""),
                    candidateassessmentreview__isnull=True,
                )
            else:
                queryset = queryset.exclude(
                    Q(note__isnull=True) | Q(note=""),
                    candidateassessmentreview__isnull=True,
                )
        return queryset


class CandidateAssessmentReviewAdmin(admin.StackedInline):
    model = CandidateAssessmentReview
    extra = 1


@admin.register(CandidateAssessment)
class CandidateAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "candidate",
        "get_score",
        "meta_information",
        "get_candidate_feedback",
        "meta_review",
        "preview_url",
    )
    search_fields = (
        "score",
        "note",
        "candidate_job__candidate__full_name",
        "candidate_job__candidate__email",
        "candidate_job__candidate__phone",
        "candidate_job__additional_message",
        "candidateassessmentreview__note",
    )
    list_filter = (
        "candidate_job__job__title",
        "assessment",
        "exam_started_at",
        "can_start_after",
        CandidateHasUrlFilter,
        CandidateHasMetaReviewFilter,
        "candidate_job__candidate__gender",
    )
    list_display_links = ("get_score",)
    ordering = ("-exam_started_at",)
    actions = (
        "send_default_sms",
        "mark_as_fail",
        "send_ct_time_extend_email",
        "send_email",
    )
    list_per_page = 50
    inlines = (CandidateAssessmentReviewAdmin,)
    autocomplete_fields = (
        "candidate_job",
        "assessment",
    )
    date_hierarchy = "exam_started_at"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self.request = request
        qs = qs.select_related(
            "candidate_job__candidate",
            "candidate_job__job",
            "assessment",
        )
        qs = qs.prefetch_related(
            Prefetch(
                "candidateassessmentreview_set",
                queryset=CandidateAssessmentReview.objects.select_related("created_by"),
                to_attr="cached_reviews",
            )
        )
        return qs

    class Media:
        css = {"all": ("css/list.css",)}
        js = ("js/list.js",)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and not request.user.has_perm(
            "job_board.access_candidate_evaluation_url"
        ):
            fields = [field.name for field in obj.__class__._meta.fields]
            fields.remove(
                "score",
            )
            return fields

        if not request.user.is_superuser and request.user.has_perm(
            "job_board.access_candidate_evaluation_url"
        ):
            fields = [field.name for field in obj.__class__._meta.fields]
            fields.remove(
                "score",
            )
            fields.remove(
                "evaluation_url",
            )
            return fields

        return ["step", "candidate_feedback"]

    @admin.action(description="Send Email")
    def send_email(self, request, queryset):
        candidate_email_list = [
            candidate_email.candidate_job.candidate.email
            for candidate_email in queryset
        ]
        hour = 0
        chunk_size = 50
        candidate_email_instance = CandidateEmail.objects.filter(
            by_default=True
        ).first()
        attachmentqueryset = CandidateEmailAttatchment.objects.filter(
            candidate_email=candidate_email_instance
        )
        attachment_paths = [
            attachment.attachments.path for attachment in attachmentqueryset
        ]
        if candidate_email_instance:
            chunks = [
                candidate_email_list[i : i + chunk_size]
                for i in range(0, len(candidate_email_list), chunk_size)
            ]

            # Schedule tasks for sending emails in chunks with a delay of one hour between each chunk
            for i, chunk in enumerate(chunks):
                print(chunk)
                schedule(
                    "job_board.tasks.send_chunked_emails",
                    chunk,
                    candidate_email_instance.id,
                    attachment_paths,
                    next_run=timezone.now() + timedelta(hours=hour),
                )
                hour += 1

            messages.success(request, "Email has sent successfully.")
        else:
            messages.error(
                request,
                "No default candidate email instance found. Cannot send emails.",
            )

    @admin.display()
    def candidate(self, obj):
        html_template = get_template(
            "admin/candidate_assessment/list/col_candidate.html"
        )
        html_content = html_template.render(
            {
                "candidate": obj.candidate_job.candidate,
                "candidate_job": obj.candidate_job,
                "candidate_assessment": obj,
                "request": self.request,
            }
        )
        return format_html(html_content)

    @admin.display(description="Assessment")
    def get_assessment(self, obj):
        html_template = get_template(
            "admin/candidate_assessment/list/col_assessment.html"
        )
        html_content = html_template.render({"assessment": obj.assessment})
        return format_html(html_content)

    @admin.display(description="👁")
    def preview_url(self, obj):
        html_template = get_template(
            "admin/candidate_assessment/list/col_prev_assessment.html"
        )
        html_content = html_template.render({"candidate_assessment": obj})
        return format_html(html_content)

    @admin.display(description="score/start/apply", ordering="score")
    def get_score(self, obj: CandidateAssessment):
        exam_time = ""
        if obj.exam_end_at:
            exam_time_diff = obj.exam_end_at - obj.exam_started_at
            days, hours, minutes = (
                exam_time_diff.days * 24,
                exam_time_diff.seconds // 3600,
                exam_time_diff.seconds // 60 % 60,
            )
            exam_time = days + hours + float(f"0.{minutes}")
        html_template = get_template("admin/candidate_assessment/list/col_score.html")
        html_content = html_template.render(
            {"candidate_assessment": obj, "exam_time": exam_time}
        )
        return format_html(html_content)

    @admin.display(ordering="exam_started_at")
    def meta_information(self, obj: CandidateAssessment):
        html_template = get_template(
            "admin/candidate_assessment/list/col_meta_information.html"
        )
        html_content = html_template.render({"candidate_assessment": obj})
        return format_html(html_content)

    @admin.display(description="Candidate Feedback")
    def get_candidate_feedback(self, obj: CandidateAssessment):
        html_template = get_template(
            "admin/candidate_assessment/list/col_candidate_feedback.html"
        )
        html_content = html_template.render({"candidate_assessment": obj})
        return format_html(html_content)
        # html_content = html_template.render(
        #     {
        #         "candidate_assessment": obj.candidate_feedback.replace("{", "_").replace("}", "_") if obj.candidate_feedback is not None else None
        #     }
        # )
        #
        # try:
        #     data = format_html(html_content)
        # except:
        #     data = "-"
        #
        # return data

    @admin.display(ordering="updated_at")
    def meta_review(self, obj: CandidateAssessment):
        reviews = getattr(obj, "cached_reviews", [])
        html_template = get_template(
            "admin/candidate_assessment/list/col_meta_review.html"
        )
        html_content = html_template.render(
            {
                "candidate_assessment": obj,
                "reviews": reviews,
            }
        )
        return format_html(html_content)

    def get_urls(self):
        urls = super().get_urls()
        candidate_assessment_urls = [
            path(
                "candidate-assessment/<int:assessment__id__exact>/preview/",
                self.admin_site.admin_view(self.preview_assessment),
                name="candidate.assessment.preview",
            )
        ]
        return candidate_assessment_urls + urls

    def preview_assessment(self, request, *args, **kwargs):
        candidate_assessment = CandidateAssessment.objects.get(
            id=kwargs.get("assessment__id__exact")
        )
        context = dict(
            self.admin_site.each_context(request),
            candidate_assessment=candidate_assessment,
            title=f"{candidate_assessment.assessment} - {candidate_assessment.candidate_job.candidate}",
        )
        return TemplateResponse(
            request,
            "admin/candidate_assessment/assessment_preview.html",
            context=context,
        )

    @admin.display(description="Send Default Promotional SMS")
    def send_default_sms(self, request, queryset):
        promotion = SMSPromotion.objects.filter(is_default=True).first()
        if promotion:
            for candidate_assessment in queryset:
                async_task(
                    "job_board.tasks.sms_promotion",
                    promotion.sms_body,
                    candidate_assessment,
                    group=f"{candidate_assessment.candidate_job.candidate} Got an Promotional SMS",
                )

    @admin.display(description="Mark as Fail / Withdraw Application")
    def mark_as_fail(self, request, queryset: QuerySet(CandidateAssessment)):
        for candidate_assessment in queryset:
            candidate_assessment.can_start_after = timezone.now()
            candidate_assessment.exam_started_at = timezone.now()
            candidate_assessment.exam_end_at = timezone.now()
            candidate_assessment.score = -1.0
            candidate_assessment.evaluation_url = None
            candidate_assessment.note = "System Generated Failed / Withdraw"
            candidate_assessment.save()

    @admin.action(description="Send Coding Test Time Extend Email")
    def send_ct_time_extend_email(self, request, queryset):
        for candidate_assesment in queryset:
            candidate_pk = candidate_assesment.candidate_job.candidate.pk
            # management.call_command('send_ct_time_extend_email', candidate_pk, candidate_assesment)
            management.call_command("send_ct_time_extend_email", candidate_pk)
            messages.success(request, "Mail Sent Successfully.")


@admin.register(ResetPassword)
class CandidateResetPasswordAdmin(admin.ModelAdmin):
    list_display = ("email", "otp", "otp_expire_at", "otp_used_at")
    readonly_fields = ("otp", "otp_expire_at", "otp_used_at")

    def has_module_permission(self, request):
        return False


@admin.register(JobPreferenceRequest)
class JobPreferenceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "preferred_designation",
        "cv",
        "created_at",
    )  # Display these fields in the admin list
    search_fields = [
        "email",
        "preferred_designation",
    ]  # Enable searching by these fields

    def has_module_permission(self, request):
        return False
