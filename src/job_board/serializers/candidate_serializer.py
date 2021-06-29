from rest_framework.fields import ReadOnlyField
from rest_framework.serializers import ModelSerializer

from job_board.models import Candidate, CandidateJob
from job_board.serializers.job_serializer import JobSerializer


class CandidateSerializer(ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('id', 'username', 'email', 'phone', 'password', 'avatar', 'cv')


class CandidateJobSerializer(ModelSerializer):
    job_title = ReadOnlyField(source="job.title")
    job_slug = ReadOnlyField(source="job.slug")
    job = JobSerializer(many=False)

    class Meta:
        model = CandidateJob
        fields = '__all__'
        read_only_fields = ['mcq_exam_score', 'written_exam_score', 'viva_exam_score']
        write_only = ['job', 'candidate']
