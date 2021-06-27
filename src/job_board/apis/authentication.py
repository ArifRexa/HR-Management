import jwt
from django.contrib.auth import hashers
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from job_board.models import Candidate
from job_board.serializers import CandidateSerializer, CredentialsSerializer


class CandidateRegistration(CreateModelMixin, GenericAPIView):
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
        serializer = CredentialsSerializer(data=request.data)
        if serializer.is_valid():
            return self.__auth_token(serializer)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def __auth_token(self, serializer: CredentialsSerializer):
        candidate = Candidate.objects.get(email=serializer.data['email'])
        if hashers.check_password(serializer.data['password'], candidate.password):
            return self.__generate_token(candidate)
        return Response({'error': 'Credentials does not matched'}, status=status.HTTP_401_UNAUTHORIZED)

    def __generate_token(self, candidate: Candidate):
        user_serializer = CandidateSerializer(candidate)
        encoded = jwt.encode(user_serializer.data, "rifat", algorithm="HS256")
        return Response({'_token': encoded})
