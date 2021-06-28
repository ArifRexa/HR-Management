import datetime

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from job_board.auth.CandidateAuth import CandidateAuth
from job_board.models import Job, CandidateJob
from job_board.serializers import JobSerializer, CandidateJobSerializer


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


class CandidateJobView(CreateModelMixin, ListModelMixin, GenericJobView):
    queryset = CandidateJob.objects.all()
    serializer_class = CandidateJobSerializer

    authentication_classes = [CandidateAuth]

    def post(self, request, *args, **kwargs):
        # TODO : candidate should not able to re-apply for the same position in a month
        request.data['job'] = Job.objects.get(slug__exact=request.data['job']).pk
        request.data["candidate"] = request.user.id
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.queryset.filter(candidate_id=request.user.id)  # TODO : this will be auth id
        return self.list(request, *args, **kwargs)

    def __not_allied(self):
        pass
        # CandidateJobs.objects.filter(created_at__gt=)
