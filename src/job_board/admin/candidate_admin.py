from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from job_board.models import Candidate, CandidateJob, ResetPassword, CandidateAssessment


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    change_form_template = 'admin/candidate/custom_candidate_form.html'

    list_display = ('full_name', 'email', 'phone', 'applied_job')

    def applied_job(self, obj: Candidate):
        return obj.candidatejob_set.count()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['candidate_jobs'] = CandidateJob.objects.filter(candidate_id=object_id).all()
        return super(CandidateAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(CandidateJob)
class CandidateJobAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'get_job', 'get_assessment', 'unique_id')
    list_display_links = ('get_job', 'candidate')

    @admin.display(description='Job', ordering='job')
    def get_job(self, obj):
        return obj.job.title

    @admin.display(description='Assessment', ordering='job__assessment')
    def get_assessment(self, obj: CandidateJob):
        url = reverse(f'admin:{obj.job.assessment._meta.app_label}_{obj.job.assessment._meta.model_name}_change',
                      args=[obj.job.assessment.id])
        return format_html(
            f'<a href="{url}">{obj.job.assessment}</a>'
        )


@admin.register(CandidateAssessment)
class CandidateAssessment(admin.ModelAdmin):
    list_display = ('candidate_job', 'assessment', 'exam_started_at', 'exam_type', 'score', 'step')
    search_fields = ('score', 'candidate_job__candidate__full_name', 'candidate_job__candidate__email')
    list_filter = ('assessment', 'exam_type', 'candidate_job__job')
    readonly_fields = ['step']


@admin.register(ResetPassword)
class CandidateResetPasswordAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'otp_expire_at', 'otp_used_at')
    readonly_fields = ('otp', 'otp_expire_at', 'otp_used_at')
