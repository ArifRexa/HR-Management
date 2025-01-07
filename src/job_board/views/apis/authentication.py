from django.contrib.auth import hashers
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from job_board.models import Candidate
from rest_framework.permissions import IsAdminUser
from datetime import datetime
from django.utils.timezone import make_aware
from config import settings
from job_board.auth.CandidateAuth import CandidateAuth, CredentialsSerializer
from job_board.models.candidate import Candidate, CandidateJob
from job_board.models.job import Job
from job_board.serializers.candidate_serializer import CandidateSerializer, CandidateUpdateSerializer
from job_board.serializers.password_reset import SendOTPSerializer, ResetPasswordSerializer, ChangePasswordSerializer
from job_board.tasks import send_interview_email, send_cancellation_email


class Registration(CreateModelMixin, GenericAPIView):
    """
    Candidate registration requires a form data with
    """
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class Login(GenericAPIView, CreateModelMixin):
    """
    Candidate Login

    candidate only can able to login with email & password

    send a post request with a valid json format { "email" : "<your@email>", "password": "<your password>" }
    """

    serializer_class = CredentialsSerializer

    def post(self, request, format=None):
        auth = CandidateAuth()
        return auth.auth_token(request)


class User(APIView):
    """
    Candidate information
    TODO : update profile update will be in post method
    """
    authentication_classes = [CandidateAuth]

    def get(self, request, format=None):
        serialize = CandidateSerializer(request.user, context={"request": request})
        return Response(serialize.data)

    def post(self, request, format=None):
        serialize = CandidateUpdateSerializer(data=request.data, context={'request': request})
        if serialize.is_valid():
            serialize.update(instance=request.user, validated_data=serialize.validated_data)
            return Response(serialize.data)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOTP(GenericAPIView, CreateModelMixin):
    serializer_class = SendOTPSerializer
    queryset = Candidate.objects.all()

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({'message': 'OTP has been sent'}, status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView, CreateModelMixin):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({'message': 'Candidate password has been updated successfully'})


class ChangeCandidatePassword(APIView):
    authentication_classes = [CandidateAuth]

    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.update(instance=request.user, validated_data=serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateShortlistView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, candidate_id):
        print(f"Received request for candidate {candidate_id}")  # Debug print
        print(f"Request data: {request.data}")  # Debug print
        all_jobs = Job.objects.all()
        print("*"*100)
        for job in all_jobs:
            print(job)
        # print(all_jobs)
        print("-"*10)
        candidate_all = CandidateJob.objects.all()
        for candidate in candidate_all:
            print(candidate)
            print(candidate.candidate.email)
        print(candidate_all)
        try:
            candidate = get_object_or_404(Candidate, id=candidate_id)
            candidate.is_shortlisted = request.data.get('is_shortlisted')
            candidate.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")  # Debug print
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateCallView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        candidate.is_called = request.data.get('is_called')
        candidate.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class UpdateScheduleView(APIView):
    permission_classes = [IsAdminUser]

    # def post(self, request, candidate_id):
    #     candidate = get_object_or_404(Candidate, id=candidate_id)
    #     candidate.schedule_datetime = request.data.get('schedule_datetime')
    #     candidate.save()
    #     return Response({'status': 'success'}, status=status.HTTP_200_OK)
    def post(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        schedule_datetime = request.data.get('schedule_datetime')

        if schedule_datetime:  # Update with new value
            candidate.schedule_datetime = schedule_datetime
        else:  # Reset to null if cancel is triggered
            candidate.schedule_datetime = None

        candidate.save()
        print(candidate.schedule_datetime)
        if candidate.schedule_datetime:
            send_interview_email(candidate.id, candidate.schedule_datetime)
        else:
            send_cancellation_email(candidate.id)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class UpdateFeedbackView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        candidate.feedback = request.data.get('feedback')
        candidate.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class UpdateStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        candidate.application_status = request.data.get('application_status')
        candidate.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
