from django.contrib import admin

from job_board.models import JobSummery, Job, JobAdditionalField


class JobSummeryInline(admin.StackedInline):
    model = JobSummery
    min_num = 1


class AdditionalFieldInline(admin.TabularInline):
    model = JobAdditionalField

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    inlines = (JobSummeryInline, AdditionalFieldInline)
    list_display = ('title', 'job_summery',)
