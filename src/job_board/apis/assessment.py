import uuid
from uuid import UUID

from django.utils import timezone
from rest_framework import generics, status, serializers
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from job_board.models import CandidateJob, AssessmentQuestion, Job
from job_board.serializers.assessment_serializer import AssessmentQuestionSerializer, GivenAssessmentAnswerSerializer
from job_board.serializers.candidate_serializer import CandidateJobSerializer


class AssessmentRetrieve(GenericAPIView, RetrieveModelMixin):
    serializer_class = CandidateJobSerializer
    queryset = CandidateJob.objects.all()
    lookup_field = 'unique_id'
    candidate_job = CandidateJob

    def get(self, request, *args, **kwargs):
        candidate_job = self.retrieve(request, *args, **kwargs)
        job = Job.objects.filter(pk=candidate_job.data['job']).first()
        self.start_exam(candidate_job.data['unique_id'], job)
        questions = AssessmentQuestionSerializer(
            job.assessment.assessmentquestion_set.filter(pk=self._get_question_id_by_step()).first())
        return Response({
            'uuid': self.candidate_job.unique_id,
            'title': job.assessment.title,
            'duration': job.assessment.duration,
            'started_at': self.candidate_job.mcq_exam_started_at,
            'time_spend': '',
            'step': self.candidate_job.step,
            'question': questions.data
        })

    def start_exam(self, unique_id: UUID, job: Job):
        candidate_job = CandidateJob.objects.filter(unique_id=unique_id).first()
        if not candidate_job.mcq_exam_started_at:
            candidate_job.mcq_exam_started_at = timezone.now()
            candidate_job.step = {
                'current_step': 0,
                'question_ids': list(job.assessment.assessmentquestion_set.values_list('id', flat=True))
            }
            candidate_job.save()
        self.candidate_job = candidate_job

    def _get_question_id_by_step(self):
        if len(self.candidate_job.step['question_ids']) == self.candidate_job.step['current_step']:
            raise serializers.ValidationError({'exam_complete': 'All step done'})
        return self.candidate_job.step['question_ids'][self.candidate_job.step['current_step']]


class SaveAnswerView(GenericAPIView, CreateModelMixin):
    serializer_class = GivenAssessmentAnswerSerializer

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({'d': 'd'})
