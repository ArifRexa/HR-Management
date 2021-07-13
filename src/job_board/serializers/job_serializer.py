from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from job_board.models import JobSummery, Job


class JobSummerySerializer(serializers.ModelSerializer):
    application_deadline = serializers.DateField(format="%B %d %Y")
    job_type = serializers.CharField(source='get_job_type_display')

    class Meta:
        model = JobSummery
        fields = ['application_deadline', 'experience', 'job_type', 'vacancy']


class JobSerializer(serializers.ModelSerializer):
    job_summery = JobSummerySerializer(many=False)
    updated_at = serializers.DateTimeField(format="%B %d %Y")

    # assessment = AssessmentSerializer(many=False)

    class Meta:
        model = Job
        fields = ['title', 'slug', 'job_context', 'job_description', 'job_responsibility',
                  'educational_requirement', 'additional_requirement', 'compensation', 'job_summery', 'assessment',
                  'updated_at']
