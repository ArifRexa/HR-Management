from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models

from job_board.models.assessment import Assessment
from job_board.models.job import JobContext, JobSummery, JobAdditionalField, Job


class JobSummeryInline(admin.StackedInline):
    model = JobSummery
    min_num = 1


class JobContextInline(admin.TabularInline):
    model = JobContext
    extra = 1


class AdditionalFieldInline(admin.TabularInline):
    model = JobAdditionalField

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1


class JobForm(forms.ModelForm):
    assessments = forms.ModelMultipleChoiceField(
        queryset=Assessment.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='assessments', is_stacked=False)
    )

    class Meta:
        model = Job
        fields = '__all__'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    inlines = (JobSummeryInline, JobContextInline, AdditionalFieldInline)
    list_display = ('title', 'job_summery', 'active')
    form = JobForm
    actions = ('clone_job',)

    @admin.action(description='Clone Job')
    def clone_job(self, request, queryset):
        job = queryset.first()
        if job:
            job_summery = job.job_summery
            job_contexts = job.job_contexts.all()
            job_additional_fields = job.additional_fields.all()
            self.clone_job_object_with_related(job, job_summery, job_contexts, job_additional_fields)

    def clone_job_object_with_related(self, job, job_summery, job_contexts, job_additional_fields):
        print(job_contexts)
        print(job_additional_fields)
        job.pk = None
        job.title = f'{job.title} (copy)'
        job.save()
        job_summery.pk = None
        job_summery.job_id = job.id
        job_summery.save()
        for job_context in job_contexts:
            job_context.pk = None
            job_context.job_id = job.id
            job_context.save()

        for job_additional_field in job_additional_fields:
            job_additional_field.pk = None
            job_additional_field.job_id = job.id
            job_additional_field.save()
