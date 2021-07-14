from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from job_board.auth.CandidateAuth import CandidateAuth
from job_board.models import Candidate
from job_board.serializers.candidate_serializer import CandidateSerializer


class Registration(CreateModelMixin, GenericAPIView):
    """
    Candidate registration requires a form data with
    """
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class Login(APIView):
    """
    Candidate Login

    candidate only can able to login with email & password

    send a post request with a valid json format { "email" : "<your@email>", "password": "<your password>" }
    """

    def post(self, request, format=None):
        auth = CandidateAuth()
        return auth.auth_token(request)


class User(APIView):
    authentication_classes = [CandidateAuth]

    def get(self, request, format=None):
        serialize = CandidateSerializer(request.user, context={"request": request})
        return Response(serialize.data)
