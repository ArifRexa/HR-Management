from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from job_board.models import Job
from job_board.serializers import JobSerializer


class ActiveJobList(APIView):
    """
    Returns a list of all **jobs** in the system

    For more details on how get single job [see here][ref].

    [ref]: /api/jobs/details/slug
    """

    def get(self, request, format=None):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)


class JobDetail(APIView):
    """
    Return job by job slug in the system
    """

    def get_object(self, slug):
        try:
            return Job.objects.get(slug__exact=slug)
        except:
            raise Http404

    def get(self, request, slug, format=None):
        job = self.get_object(slug)
        serializer = JobSerializer(job)
        return Response(serializer.data)
