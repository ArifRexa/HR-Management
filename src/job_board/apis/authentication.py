from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from job_board.models import Candidate
from job_board.serializers import CandidateSerializer


class CandidateRegistration(CreateModelMixin, RetrieveModelMixin, GenericAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class Login(APIView):
    def post(self, request):
        print(request.data)
        return Response(request.data)
