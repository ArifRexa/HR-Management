from django import forms
from django.contrib import admin
from django.contrib.auth import hashers
from django.utils.html import format_html, linebreaks

from config import settings
from job_board.models.candidate import Candidate, CandidateJob, ResetPassword, CandidateAssessment


class CandidateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), strip=False, required=False)

    class Meta:
        model = Candidate
        fields = "__all__"


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    change_form_template = 'admin/candidate/custom_candidate_form.html'
    search_fields = ('full_name', 'email', 'phone')
    list_display = ('contact_information', 'assessment', 'note', 'expected_salary')
    list_filter = ('candidatejob__merit', 'candidatejob__job')

    @admin.display(ordering='candidatejob__expected_salary')
    def expected_salary(self, obj: Candidate):
        candidate_job = obj.candidatejob_set.last()
        if candidate_job is not None:
            return candidate_job.expected_salary

    @admin.display(ordering='full_name')
    def contact_information(self, obj: Candidate):
        return format_html(
            f'{obj.full_name} <br>'
            f'{obj.email} <br>'
            f'{obj.phone} <br>'
        )

    @admin.display()
    def assessment(self, obj: Candidate):
        assessments = ''
        candidate_job = obj.candidatejob_set.last()
        if candidate_job is not None:
            for candidate_assessment in candidate_job.candidate_assessment.all():
                assessments += f'<span style="color : {"green" if candidate_assessment.result == "pass" else ""}">' \
                               f'{candidate_assessment.assessment} ' \
                               f'| {candidate_assessment.score} out of {candidate_assessment.assessment.score}' \
                               f'</span><br>'
        return format_html(assessments)

    @admin.display()
    def note(self, obj: Candidate):
        candidate_job = obj.candidatejob_set.last()
        if candidate_job:
            return format_html(linebreaks(candidate_job.additional_message))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['candidate_jobs'] = CandidateJob.objects.filter(candidate_id=object_id).all()
        return super(CandidateAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        try:
            print(hashers.identify_hasher(request.POST['password']))
            super(CandidateAdmin, self).save_model(request, obj, form, change)
        except:
            obj.password = hashers.make_password(request.POST['password'], settings.CANDIDATE_PASSWORD_HASH)
            super(CandidateAdmin, self).save_model(request, obj, form, change)


@admin.register(CandidateJob)
class CandidateJobAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'get_job', 'expected_salary', 'get_assessment', 'additional_message', 'merit')
    list_display_links = ('get_job', 'candidate')
    search_fields = ('candidate__full_name', 'candidate__email', 'candidate__phone')
    list_filter = ('merit', 'job', 'candidate_assessment__assessment')

    @admin.display(description='Job', ordering='job')
    def get_job(self, obj):
        return obj.job.title

    @admin.display(description='Assessment', ordering='job__assessment')
    def get_assessment(self, obj: CandidateJob):
        assessment_result = ''
        for ddd in obj.candidate_assessment.all():
            assessment_result += f'{ddd.assessment} {ddd.result} {ddd.score} <br>'
        return format_html(assessment_result)


@admin.register(CandidateAssessment)
class CandidateAssessmentAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'exam_started_at', 'get_assessment', 'score', 'status',
                    'result', 'preview_assessment', 'unique_id')
    search_fields = ('score', 'candidate_job__candidate__full_name', 'candidate_job__candidate__email')
    list_filter = ('assessment', 'assessment__type', 'candidate_job__job__title')

    readonly_fields = ['step']

    @admin.display()
    def candidate(self, obj):
        return format_html(
            f'{obj.candidate_job.candidate.full_name}'
        )

    @admin.display()
    def get_assessment(self, obj):
        return format_html(
            f'{obj.assessment.title} </br>'
            f'Total Score : {obj.assessment.score} </br>'
            f'Pass Score : {obj.assessment.pass_score} </br>'
            f'{obj.assessment.get_type_display()}'
        )

    @admin.display()
    def assessment_pass_score(self, obj):
        return obj.assessment.pass_score

    @admin.display(description='👁')
    def preview_assessment(self, obj):
        if obj.assessment.open_to_start:
            return 'own url'
        else:
            return obj.evaluation_url


@admin.register(ResetPassword)
class CandidateResetPasswordAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'otp_expire_at', 'otp_used_at')
    readonly_fields = ('otp', 'otp_expire_at', 'otp_used_at')
