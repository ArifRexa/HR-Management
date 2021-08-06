import re

from django.contrib.auth import password_validation, hashers
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from config import settings
from job_board.models.candidate import Candidate, CandidateJob
from job_board.models.job import Job
from job_board.serializers.job_serializer import JobSerializerSimple


class CandidateSerializer(ModelSerializer):
    """
    Candidate serializer has been used in registration and fetch candidate
    this serializer is based on Candidate Model
    """
    phone = serializers.IntegerField()

    class Meta:
        model = Candidate
        fields = ('id', 'full_name', 'email', 'password', 'phone', 'avatar', 'cv')
        extra_kwargs = {'password': {"write_only": True}}

    def get_cv_url(self, candidate):
        request = self.context.get('request')
        cv_url = candidate.cv.url
        return request.build_absolute_uri(cv_url)


class CandidateUpdateSerializer(serializers.ModelSerializer):
    """
    Candidate profile update serializer, this serializer has been used in candidate profile update
    """
    current_password = serializers.CharField()

    def validate(self, data):
        user_pass = self.context['request'].user.password
        given_pass = hashers.make_password(data['current_password'], salt=settings.CANDIDATE_PASSWORD_HASH)
        if user_pass == given_pass:
            return data
        raise serializers.ValidationError({'current_password': 'Current password does not matched'})

    class Meta:
        model = Candidate
        fields = ('full_name', 'cv', 'avatar', 'current_password')
        extra_kwargs = {'cv': {'required': False}}


class CandidateJobApplySerializer(serializers.Serializer):
    job_slug = serializers.CharField()
    expected_salary = serializers.FloatField()
    additional_message = serializers.CharField(allow_null=True, allow_blank=True)
    additional_fields = serializers.ListField()

    next_message = ''

    def validate(self, data):
        job = Job.objects.filter(slug__exact=data['job_slug']).first()
        if job:
            job_additional_fields = job.additional_fields.all()
            request_additional_fields = data['additional_fields']
            if self._valid_additional_fields(job_additional_fields, request_additional_fields):
                return data
        raise serializers.ValidationError({'job_slug': 'Invalid Job slug, we could not found job by your given slug'})

    def create(self, validated_data):
        message = validated_data['additional_fields']
        validated_data.pop('job_slug')
        validated_data.pop('additional_fields')
        candidate_job = CandidateJob(**validated_data)
        candidate_job.additional_message += self.next_message
        candidate_job.save()
        return candidate_job

    def update(self, instance, validated_data):
        pass

    def _valid_additional_fields(self, job_additional_fields, request_additional_fields):
        if self._match_len(job_additional_fields, request_additional_fields):
            for index, field in enumerate(job_additional_fields):
                self.next_message += f'{field.title} : {request_additional_fields[index]} \n'
                if request_additional_fields[index]:
                    if not re.match(field.validation_regx, request_additional_fields[index]):
                        msg = f'{request_additional_fields[index]} is not a valid {field.title}'
                        raise serializers.ValidationError({f'additional_fields.{index}': msg})
                elif field.required:
                    raise serializers.ValidationError({f'additional_fields.{index}': f'{field.title} Is required'})
        return True

    @staticmethod
    def _match_len(job_additional_fields, request_additional_fields: []):
        if job_additional_fields.count() == len(request_additional_fields):
            return True
        msg = f'We are expecting {job_additional_fields.count()} but given was {len(request_additional_fields)}'
        raise serializers.ValidationError({'additional_fields': msg})


class CandidateJobSerializer(serializers.ModelSerializer):
    job = JobSerializerSimple(many=False)
    created_at = serializers.DateTimeField(format='%d %B, %Y', read_only=True, required=False)

    # candidate_assessment = "job_board.serializers.assessment_serializer.CandidateAssessmentSerializer"

    class Meta:
        model = CandidateJob
        fields = ('unique_id', 'job', 'expected_salary', 'additional_message',
                  'created_at', 'merit', 'candidate_assessment')
        depth = 2
