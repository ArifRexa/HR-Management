import json

from django.contrib.auth import hashers
from django.db.models.aggregates import Sum, Count
from django.views.decorators.csrf import csrf_exempt
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
from job_board.models.candidate import Candidate, CandidateJob, CandidateApplicationSummary
from job_board.models.job import Job
from job_board.serializers.candidate_serializer import CandidateSerializer, CandidateUpdateSerializer
from job_board.serializers.password_reset import SendOTPSerializer, ResetPasswordSerializer, ChangePasswordSerializer
from job_board.tasks import send_interview_email, send_cancellation_email, send_bulk_application_summary_email, \
    send_waiting_list_email, send_rejection_email, send_reschedule_email


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

        all_jobs = Job.objects.all()

        for job in all_jobs:
            print(job)
        # print(all_jobs)

        candidate_all = CandidateJob.objects.all()

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

    def post(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        schedule_datetime = request.data.get('schedule_datetime')

        if schedule_datetime:  # Update with new value
            candidate.schedule_datetime = schedule_datetime
        else:  # Reset to null if cancel is triggered
            candidate.schedule_datetime = None
            send_cancellation_email(candidate.id)

        candidate.save()

        # Don't send any emails here - emails will be sent when status changes to 'scheduled'
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

    # def post(self, request, candidate_id):
    #     candidate = get_object_or_404(Candidate, id=candidate_id)
    #     candidate.application_status = request.data.get('application_status')
    #     candidate.save()
    #     return Response({'status': 'success'}, status=status.HTTP_200_OK)
    def post(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        new_status = request.data.get('application_status')
        email_sent = None

        # Handle different status changes
        if new_status == 'waiting':
            email_sent = send_waiting_list_email(candidate.id)
        elif new_status == 'rejected':
            email_sent = send_rejection_email(candidate.id)
        elif new_status == 'scheduled':
            # Save the status immediately
            candidate.application_status = new_status
            candidate.save()

            # Only send email if schedule_datetime exists
            if candidate.schedule_datetime:
                send_interview_email(candidate.id, candidate.schedule_datetime)
                email_sent = True
        elif new_status == 'rescheduled':
            # Save the status immediately
            candidate.application_status = new_status
            candidate.save()

            # Schedule the email to be sent after 10 seconds
            # This allows time for schedule_datetime to be updated
            # time.sleep(10)  # Wait for 10 seconds
            email_sent = send_reschedule_email(candidate.id)
            return Response({
                'status': 'success',
                'message': 'Status updated and email scheduled',
                'email_sent': email_sent
            }, status=status.HTTP_200_OK)

        candidate.application_status = new_status
        candidate.save()

        return Response({
            'status': 'success',
            'message': 'Status updated successfully',
            'email_sent': email_sent
        }, status=status.HTTP_200_OK)


from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from datetime import datetime
from calendar import month_name



@method_decorator(staff_member_required, name='dispatch')
class ApplicationSummaryView(TemplateView):
    template_name = 'admin/application_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = datetime.now().year
        context['years'] = range(current_year, current_year - 4, -1)
        context['jobs'] = Job.objects.all()
        return context

    @staticmethod
    def get_months(request):
        jobs = request.GET.get('jobs', '').split(',')
        years = request.GET.get('years', '').split(',')

        months_data = CandidateJob.objects.filter(
            job_id__in=jobs,
            created_at__year__in=years
        ).values('created_at__month').annotate(
            count=Count('id')
        ).order_by('created_at__month')

        months = [
            {
                'month': month['created_at__month'],
                'name': month_name[month['created_at__month']],
                'count': month['count']
            }
            for month in months_data
        ]
        return JsonResponse({'months': months})

    @staticmethod
    @staff_member_required
    def get_emails(request):
        if request.method == 'POST':
            jobs = request.POST.getlist('jobs')
            years = request.POST.getlist('years')
            months = request.POST.getlist('months')

            jobwise_candidates = {}
            total_candidates = 0

            for job_id in jobs:
                try:
                    job = Job.objects.get(id=job_id)
                    candidates = CandidateJob.objects.filter(
                        job_id=job_id,
                        created_at__year__in=years,
                        created_at__month__in=months
                    ).select_related('candidate')

                    jobwise_candidates[job.title] = [cj.candidate.email for cj in candidates]
                    total_candidates += len(candidates)
                except Job.DoesNotExist:
                    continue

            return JsonResponse({
                'total_candidates': total_candidates,
                'jobwise_candidates': jobwise_candidates
            })

    @staticmethod
    @staff_member_required
    def send_emails(request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                jobwise_emails = data.get('jobwise_emails', {})
                opening_positions = data.get('opening_positions', [])

                # Convert opening positions to list of dictionaries with title and slug
                opening_positions_data = [
                    {
                        'title': pos['title'],
                        'slug': pos['slug']  # Include the slug
                    }
                    for pos in opening_positions
                ]

                for job_title, emails in jobwise_emails.items():
                    send_bulk_application_summary_email(emails, job_title, opening_positions_data)

                return JsonResponse({
                    'status': 'success',
                    'message': f'Emails sent successfully to all candidates'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)







