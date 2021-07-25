from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from rest_framework.response import Response

from job_board.auth.CandidateAuth import CandidateAuth
from job_board.models import CandidateAssessment
from job_board.serializers.assessment_serializer import GivenAssessmentAnswerSerializer, \
    CandidateAssessmentSerializer


class AssessmentRetrieve(GenericAPIView, mixins.ListModelMixin):
    serializer_class = CandidateAssessmentSerializer
    authentication_classes = [CandidateAuth]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return CandidateAssessment.objects.filter(candidate_job__candidate=user).all()


class SaveAnswerView(GenericAPIView, mixins.CreateModelMixin):
    serializer_class = GivenAssessmentAnswerSerializer
    authentication_classes = [CandidateAuth]

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({'d': 'd'})
