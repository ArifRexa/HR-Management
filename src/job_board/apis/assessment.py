from datetime import timedelta

from django.core.exceptions import BadRequest
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from job_board.auth.CandidateAuth import CandidateAuth
from job_board.models import CandidateAssessment
from job_board.serializers.assessment_serializer import GivenAssessmentAnswerSerializer, \
    CandidateAssessmentSerializer, AssessmentQuestionSerializer


class CandidateAssessmentView(GenericAPIView):
    serializer_class = CandidateAssessmentSerializer
    authentication_classes = [CandidateAuth]
    lookup_field = 'unique_id'

    def get_queryset(self):
        user = self.request.user
        return CandidateAssessment.objects.filter(candidate_job__candidate=user).all()


class CandidateAssessmentList(CandidateAssessmentView, mixins.ListModelMixin):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CandidateAssessmentRetrieve(CandidateAssessmentView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # candidate_assessment = CandidateAssessment()
        candidate_assessment = self.get_object()
        # if candidate_assessment.exam_started_at is None: # TODO : assessment must not to be updated once it's started
        candidate_assessment.exam_started_at = timezone.now()
        candidate_assessment.exam_end_at = timezone.now() + timedelta(
            minutes=candidate_assessment.assessment.duration)
        candidate_assessment.step = {
            'current_step': 0,
            'question_ids': list(candidate_assessment.assessment.assessmentquestion_set.values_list('id', flat=True))
        }
        print(candidate_assessment.exam_started_at)
        print(candidate_assessment.exam_end_at)
        candidate_assessment.save()
        return Response({'message': 'Exam started'})


class CandidateAssessmentQuestion(APIView):
    def get(self, request, *args, **kwargs):
        kwargs['exam_started_at__isnull'] = False
        try:
            candidate_assessment = CandidateAssessment.objects.filter(**kwargs).first()
            question_serializer = AssessmentQuestionSerializer(self.get_question(candidate_assessment))
            return Response(question_serializer.data)
        except BadRequest:
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

    def get_question(self, candidate_assessment: CandidateAssessment):
        question_id = candidate_assessment.step['question_ids'][candidate_assessment.step['current_step']]
        return candidate_assessment.assessment.assessmentquestion_set.filter(id=question_id).first()


class SaveAnswerView(GenericAPIView, mixins.CreateModelMixin):
    serializer_class = GivenAssessmentAnswerSerializer
    authentication_classes = [CandidateAuth]

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({'d': 'd'})
