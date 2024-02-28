from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from job_board.models import VivaConfig, JobVivaTimeSlot
from job_board.serializers import VivaConfigSerializer, JobVivaTimeSlotSerializer
from rest_framework import generics


class VivaConfigViewSet(viewsets.ModelViewSet):
    serializer_class = VivaConfigSerializer

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return VivaConfig.objects.filter(job_post_id=job_id)


class JobVivaTimeSlotViewSet(viewsets.ModelViewSet):
    serializer_class = JobVivaTimeSlotSerializer

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return JobVivaTimeSlot.objects.filter(job_post_id=job_id)


class JobVivaTimeSlotCreateAPIView(generics.CreateAPIView):
    serializer_class = JobVivaTimeSlotSerializer