from django.contrib import admin

# Register your models here.
from job_board.models import Job, JobSummery, Candidate


class JobSummeryInline(admin.StackedInline):
    model = JobSummery
    min_num = 1


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    inlines = (JobSummeryInline,)
    list_display = ('title', 'jobsummery',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'password')
