import datetime

from django import forms
from django.contrib import admin
from django.contrib.auth import hashers
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Sum
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html, linebreaks
from openpyxl.cell.cell import get_type

from config import settings
from job_board.models.candidate import Candidate, CandidateJob, ResetPassword, CandidateAssessment, \
    CandidateAssessmentAnswer


class CandidateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), strip=False, required=False)

    class Meta:
        model = Candidate
        fields = "__all__"


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    change_form_template = 'admin/candidate/custom_candidate_form.html'
    search_fields = ('full_name', 'email', 'phone')
    list_display = ('contact_information', 'assessment', 'note', 'review', 'expected_salary')
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
            f'{obj.phone} <br><br>'
            f'<a href="{obj.cv.url}" target="blank">Resume</a>'
        )

    @admin.display()
    def assessment(self, obj: Candidate):
        candidate_job = obj.candidatejob_set.last()
        if candidate_job is not None:
            html_template = get_template('admin/candidate/list/assessment.html')
            html_content = html_template.render({
                'candidate_assessments': candidate_job.candidate_assessment.all()
            })
            return html_content

    @admin.display()
    def review(self, obj: Candidate):
        review = ''
        candidate_job = obj.candidatejob_set.last()
        if candidate_job is not None:
            for candidate_assessment in candidate_job.candidate_assessment.all():
                review += f'{candidate_assessment.note if candidate_assessment.note is not None else ""} <br>'
        return format_html(review)

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
    list_display = ('candidate', 'get_job', 'expected_salary', 'get_assessment', 'meta_information', 'merit')
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

    @admin.display(description='additional_message')
    def meta_information(self, obj: CandidateJob):
        return format_html(obj.additional_message.replace('\n', '<br>'))


@admin.register(CandidateAssessment)
class CandidateAssessmentAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'get_score', 'meta_information', 'preview_url')
    search_fields = ('score', 'candidate_job__candidate__full_name', 'candidate_job__candidate__email')
    list_filter = ('assessment', 'assessment__type', 'candidate_job__job__title', 'exam_started_at')
    list_display_links = ('get_score',)
    ordering = ('-exam_started_at',)

    readonly_fields = ['step']

    @admin.display()
    def candidate(self, obj):
        html_template = get_template('admin/candidate_assessment/list/col_candidate.html')
        html_content = html_template.render({
            'candidate': obj.candidate_job.candidate,
            'candidate_job': obj.candidate_job,
            'candidate_assessment': obj
        })
        return format_html(html_content)

    @admin.display(description='Assessment')
    def get_assessment(self, obj):
        html_template = get_template('admin/candidate_assessment/list/col_assessment.html')
        html_content = html_template.render({
            'assessment': obj.assessment
        })
        return format_html(html_content)

    @admin.display(description='👁')
    def preview_url(self, obj):
        html_template = get_template('admin/candidate_assessment/list/col_prev_assessment.html')
        html_content = html_template.render({
            'candidate_assessment': obj
        })
        return format_html(html_content)

    @admin.display(description='score', ordering='score')
    def get_score(self, obj: CandidateAssessment):
        exam_time = ''
        if obj.exam_end_at:
            exam_time_diff = obj.exam_end_at - obj.exam_started_at
            days, hours, minutes = exam_time_diff.days * 24, exam_time_diff.seconds // 3600, exam_time_diff.seconds // 60 % 60
            exam_time = days + hours + float(f'0.{minutes}')
        html_template = get_template('admin/candidate_assessment/list/col_score.html')
        html_content = html_template.render({
            'candidate_assessment': obj,
            'exam_time': exam_time
        })
        return format_html(html_content)

    @admin.display(ordering='exam_started_at')
    def meta_information(self, obj: CandidateAssessment):
        return format_html(obj.candidate_job.additional_message.replace('\n', '<br>'))

    def get_urls(self):
        urls = super().get_urls()
        candidate_assessment_urls = [
            path(
                'candidate-assessment/<int:assessment__id__exact>/preview/',
                self.admin_site.admin_view(self.preview_assessment),
                name='candidate.assessment.preview'
            )
        ]
        return candidate_assessment_urls + urls

    def preview_assessment(self, request, *args, **kwargs):
        candidate_assessment = CandidateAssessment.objects.get(id=kwargs.get(*kwargs))
        context = dict(
            self.admin_site.each_context(request),
            candidate_assessment=candidate_assessment,
            title=f'{candidate_assessment.assessment} - {candidate_assessment.candidate_job.candidate}',
        )
        return TemplateResponse(request, "admin/candidate_assessment/assessment_preview.html", context=context)


@admin.register(ResetPassword)
class CandidateResetPasswordAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'otp_expire_at', 'otp_used_at')
    readonly_fields = ('otp', 'otp_expire_at', 'otp_used_at')
