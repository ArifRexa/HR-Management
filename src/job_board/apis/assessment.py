from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin

from job_board.models import Assessment, AssessmentQuestion, CandidateJob
from job_board.serializers.assessment_serializer import AssessmentQuestionSerializer
from job_board.serializers.candidate_serializer import CandidateJobSerializer


class AssessmentRetrieve(RetrieveModelMixin, GenericAPIView):
    queryset = CandidateJob.objects.all()
    serializer_class = CandidateJobSerializer
    lookup_field = 'unique_id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class AssessmentQuestionRetrieve(RetrieveModelMixin, GenericAPIView):
    queryset = AssessmentQuestion.objects.all()  # TODO : we need to validate the question slug too
    serializer_class = AssessmentQuestionSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
