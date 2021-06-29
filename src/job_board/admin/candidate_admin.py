from django.contrib import admin

from job_board.models import Candidate, CandidateJob


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    change_form_template = 'admin/candidate/custom_candidate_form.html'

    list_display = ('email', 'phone')


@admin.register(CandidateJob)
class CandidateJobAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'get_job', 'mcq_exam_score', 'written_exam_score', 'viva_exam_score')
    readonly_fields = ('mcq_exam_score', 'written_exam_score', 'viva_exam_score')

    def get_job(self, obj):
        return obj.job.title
