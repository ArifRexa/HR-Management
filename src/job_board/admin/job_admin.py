from django.contrib import admin

from job_board.models import JobSummery, Job


class JobSummeryInline(admin.StackedInline):
    model = JobSummery
    min_num = 1


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    inlines = (JobSummeryInline,)
    list_display = ('title', 'job_summery',)
