import datetime

from django.http import Http404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from job_board.auth.CandidateAuth import CandidateAuth
from job_board.models import Job, CandidateJob
from job_board.serializers.job_serializer import JobSerializer
from job_board.serializers.candidate_serializer import CandidateJobSerializer, CandidateJobApplySerializer


class GenericJobView(GenericAPIView):
    queryset = Job.objects.all()
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
            serializer.save()
            return Response({'success': 'You job application has been submitted successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        candidate_jobs = CandidateJob.objects.filter(candidate_id=request.user.id).all()
        candidate_job_serialize = CandidateJobSerializer(candidate_jobs, many=True)
        return Response(candidate_job_serialize.data)

    def get_object(self, slug):
        try:
            return Job.objects.get(slug__exact=slug)
        except Job.DoesNotExist:
            raise Http404

    def __not_allied(self):
        pass
        # CandidateJobs.objects.filter(created_at__gt=)
