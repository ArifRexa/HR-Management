from django.contrib import admin

# Register your models here.
from nested_inline.admin import NestedStackedInline, NestedTabularInline, NestedModelAdmin

from job_board.models import Job, JobSummery, Candidate, CandidateJob, Assessment, AssessmentQuestion, AssessmentAnswer


class JobSummeryInline(admin.StackedInline):
    model = JobSummery
    min_num = 1


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    inlines = (JobSummeryInline,)
    list_display = ('title', 'jobsummery',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'password')


@admin.register(CandidateJob)
class CandidateJobAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'get_job', 'mcq_exam_score', 'written_exam_score', 'viva_exam_score')
    readonly_fields = ('mcq_exam_score', 'written_exam_score', 'viva_exam_score')

    def get_job(self, obj):
        print(obj.job)
        return obj.job.title


class AssessmentAnswerInline(NestedStackedInline):
    model = AssessmentAnswer
    extra = 1
    fk_name = 'assessment_question'


class AssessmentQuestionInline(NestedTabularInline):
    model = AssessmentQuestion
    extra = 1
    fk_name = 'assessment'
    inlines = [AssessmentAnswerInline]


@admin.register(Assessment)
class AssessmentAdmin(NestedModelAdmin):
    list_display = ('title', 'score', 'duration', 'description')
    inlines = [AssessmentQuestionInline]
