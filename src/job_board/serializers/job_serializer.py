from django.db import models
from django.db.models import fields
from rest_framework import serializers
from job_board.models.job import JobContext, JobSummery, Job, JobAdditionalField

class JobContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobContext
        fields = ['title','description']


class JobSummerySerializer(serializers.ModelSerializer):
    application_deadline = serializers.DateField(format="%d %B, %Y")
    job_type = serializers.CharField(source='get_job_type_display')

    class Meta:
        model = JobSummery
        fields = ['application_deadline', 'experience', 'job_type', 'vacancy', 'salary_range']


class AdditionalFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAdditionalField
        fields = ['title', 'required', 'validation_regx']


class JobSerializer(serializers.ModelSerializer):
    job_summery = JobSummerySerializer(many=False)
    additional_fields = AdditionalFieldsSerializer(many=True)
    job_contexts = JobContextSerializer(many=True)
    updated_at = serializers.DateTimeField(format="%d %B, %Y")

    # assessment = AssessmentSerializer(many=False)

    class Meta:
        model = Job
        fields = ['title', 'slug','banner_image','updated_at',
                  'job_contexts', 'assessments','job_summery', 'additional_fields']


class JobSerializerSimple(serializers.ModelSerializer):
    # assessment = AssessmentSerializer(many=False)

    class Meta:
        model = Job
        fields = ['title']
