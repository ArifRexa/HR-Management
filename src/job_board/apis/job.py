from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from job_board.models import Job
from job_board.serializers import JobSerializer


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
