import datetime
from datetime import timedelta

from django.http import Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from job_board.auth.CandidateAuth import CandidateAuth
from job_board.models.job import Job
from job_board.models.candidate import CandidateJob, Candidate
from job_board.serializers.job_serializer import JobSerializer
from job_board.serializers.candidate_serializer import CandidateJobSerializer, CandidateJobApplySerializer


class GenericJobView(GenericAPIView):
    queryset = Job.objects.filter(active=True, job_summery__application_deadline__gte=timezone.now()).order_by('level').all()
    serializer_class = JobSerializer

    class Meta:
        abstract = True


class JobList(ListModelMixin, GenericJobView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class JobRetrieve(RetrieveModelMixin, GenericJobView):
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CandidateJobView(APIView):
    """
    List all candidate jobs, or create a new candidate job.
    """

    authentication_classes = [CandidateAuth]

    def post(self, request, *args, **kwargs):
        serializer = CandidateJobApplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['candidate'] = request.user
            serializer.validated_data['job'] = self.get_object(serializer.validated_data['job_slug'])
            if not self.__applied_before(serializer.validated_data['candidate'], serializer.validated_data['job']):
                serializer.save()
                return Response({'success': 'You job application has been submitted successfully'})
            return Response(
                {'message': f'You applied for the same position less then {settings.APPLY_SAME_JOB_AFTER} days before, '
                            f'unfortunately you cannot re-apply before '
                            f'{settings.APPLY_SAME_JOB_AFTER} days of your last application'},
                status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        candidate_jobs = CandidateJob.objects.filter(candidate_id=request.user.id).order_by('-id').all()
        candidate_job_serialize = CandidateJobSerializer(candidate_jobs, many=True)
        return Response(candidate_job_serialize.data)

    def get_object(self, slug):
        """
        Get job by slug
        or it will raise 404 not found exception
        @param slug:
        @return Job | Http404:
        """
        try:
            return Job.objects.get(slug__exact=slug, active=True)
        except Job.DoesNotExist:
            raise Http404

    def __applied_before(self, candidate: Candidate, job: Job):
        """
        It will check if the candidate apply for the same position before settings.APPLY_SAME_JOB_AFTER
        or it will take 90 days as default

        @param candidate:
        @param job:
        @return:
        """
        days_before = timezone.now() - timedelta(days=settings.APPLY_SAME_JOB_AFTER or 90)
        if CandidateJob.objects.filter(candidate=candidate, job=job, created_at__gte=days_before):
            return True
        return False
