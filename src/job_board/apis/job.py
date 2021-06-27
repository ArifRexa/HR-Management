import jwt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import detail
from rest_framework.authentication import TokenAuthentication, BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from job_board.decorators import admin_required
from job_board.models import Job, CandidateJobs
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


class Test(BaseAuthentication):
    def authenticate(self, request):
        token = get_authorization_header(request).split()
        try:
            user = jwt.decode(token[1], "rifat", algorithms="HS256")
        except:
            raise AuthenticationFailed('Invalid jwt')
        return user, None


class CandidateJobView(CreateModelMixin, ListModelMixin, GenericJobView):
    queryset = CandidateJobs.objects.all()
    serializer_class = CandidateJobSerializer
    authentication_classes = [Test]

    def post(self, request, *args, **kwargs):
        request.data['job'] = Job.objects.get(slug=request.data['job']).pk
        request.data['candidate'] = 6  # TODO : this id will be auth id
        return self.create(request, args, kwargs)

    def get(self, request, *args, **kwargs):
        print(request.user)
        # request.user = 'd'
        # print(self.queryset.filter(candidate_id=6))  # TODO : this will be auth id
        return self.list(request, *args, **kwargs)
