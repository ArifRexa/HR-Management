from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, strip_tags
from nested_inline.admin import NestedStackedInline, NestedTabularInline, NestedModelAdmin

from job_board.models import AssessmentAnswer, AssessmentQuestion, Assessment


class AssessmentAnswerInline(admin.TabularInline):
    model = AssessmentAnswer
    extra = 2
    fk_name = 'assessment_question'


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'score', 'duration', 'get_description', 'type', 'show_action')

    # inlines = [AssessmentQuestionInline]

    # readonly_fields = ['score']
    @admin.display(description='description')
    def get_description(self, obj):
        return strip_tags(obj.description)

    @admin.display(description='Actions')
    def show_action(self, obj):
        return format_html(
            f'<a href="{reverse("preview_assessment", kwargs={"pk": obj.pk})}">Preview</a>'
        )


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'title', 'score', 'type')
    list_filter = ('assessment',)
    inlines = (AssessmentAnswerInline,)

    def regroup_by(self):
        return 'assessment'
