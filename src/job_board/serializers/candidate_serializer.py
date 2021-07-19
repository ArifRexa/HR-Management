from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from job_board.models import Candidate, CandidateJob, Job
from job_board.serializers.job_serializer import JobSerializer


class CandidateSerializer(ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('id', 'full_name', 'email', 'password', 'phone', 'avatar', 'cv')
        write_only_fields = ['password']

    def get_cv_url(self, candidate):
        request = self.context.get('request')
        cv_url = candidate.cv.url
        return request.build_absolute_uri(cv_url)


class CandidateJobApplySerializer(serializers.Serializer):
    job_slug = serializers.CharField()
    expected_salary = serializers.FloatField()
    additional_message = serializers.CharField(allow_null=True)

    def create(self, validated_data):
        validated_data.pop('job_slug')
        candidate_job = CandidateJob(**validated_data)
        candidate_job.save()
        return candidate_job

    def update(self, instance, validated_data):
        pass


class CandidateJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateJob
        fields = '__all__'
