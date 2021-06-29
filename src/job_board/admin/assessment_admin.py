from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedTabularInline, NestedModelAdmin

from job_board.models import AssessmentAnswer, AssessmentQuestion, Assessment


class AssessmentAnswerInline(NestedStackedInline):
    model = AssessmentAnswer
    extra = 0
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
