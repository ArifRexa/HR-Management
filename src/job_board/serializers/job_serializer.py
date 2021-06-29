from rest_framework.serializers import ModelSerializer

from job_board.models import JobSummery, Job


class JobSummerySerializer(ModelSerializer):
    class Meta:
        model = JobSummery
        fields = ['application_deadline', 'experience', 'job_type', 'vacancy']


class JobSerializer(ModelSerializer):
    job_summery = JobSummerySerializer(many=False)

    # assessment = AssessmentSerializer(many=False)

    class Meta:
        model = Job
        fields = ['title', 'slug', 'job_context', 'job_description', 'job_responsibility',
                  'educational_requirement', 'additional_requirement', 'compensation', 'job_summery', 'assessment']
