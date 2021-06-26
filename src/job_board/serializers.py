from rest_framework import serializers

from job_board.models import Job, JobSummery


class JobSummerySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSummery
        fields = ['application_deadline', 'experience', 'job_type', 'vacancy']


class JobSerializer(serializers.ModelSerializer):
    jobsummery = JobSummerySerializer(many=False)

    class Meta:
        model = Job
        # fields = '__all__'
        fields = ['title', 'slug', 'job_context', 'job_description', 'job_responsibility',
                  'educational_requirement',
                  'additional_requirement', 'compensation', 'jobsummery']
