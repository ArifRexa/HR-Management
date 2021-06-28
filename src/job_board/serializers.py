from rest_framework import serializers
from rest_framework.fields import ReadOnlyField, EmailField, CharField, JSONField, SerializerMethodField
from rest_framework.serializers import Serializer, ModelSerializer

from job_board.models import Job, JobSummery, Candidate, CandidateJob


class JobSummerySerializer(ModelSerializer):
    class Meta:
        model = JobSummery
        fields = ['application_deadline', 'experience', 'job_type', 'vacancy']


class JobSerializer(ModelSerializer):
    jobsummery = JobSummerySerializer(many=False)

    class Meta:
        model = Job
        fields = ['title', 'slug', 'job_context', 'job_description', 'job_responsibility',
                  'educational_requirement',
                  'additional_requirement', 'compensation', 'jobsummery']


class CandidateSerializer(ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('id', 'username', 'email', 'phone', 'password', 'avatar', 'cv')


class CandidateJobSerializer(ModelSerializer):
    job_title = ReadOnlyField(source="job.title")
    job_slug = ReadOnlyField(source="job.slug")

    class Meta:
        model = CandidateJob
        fields = '__all__'
        read_only_fields = ['mcq_exam_score', 'written_exam_score', 'viva_exam_score']
        write_only = ['job', 'candidate']
