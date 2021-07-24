from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from nested_inline.admin import NestedStackedInline, NestedTabularInline, NestedModelAdmin

from job_board.models import AssessmentAnswer, AssessmentQuestion, Assessment


class AssessmentAnswerInline(NestedTabularInline):
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
    list_display = ('title', 'score', 'duration', 'description', 'show_action')
    inlines = [AssessmentQuestionInline]

    # readonly_fields = ['score']

    @admin.display(description='Actions')
    def show_action(self, obj):
        return format_html(
            f'<a href="{reverse("preview_assessment", kwargs={"pk": obj.pk})}">Preview</a>'
        )
