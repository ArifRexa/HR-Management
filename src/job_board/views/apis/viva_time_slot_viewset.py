from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from job_board.models import VivaConfig, JobVivaTimeSlot
from job_board.serializers import VivaConfigSerializer, JobVivaTimeSlotSerializer
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination


# class CustomHighestFivePagination(PageNumberPagination):
#     page_size = 5
#
#     def paginate_queryset(self, queryset, request, view=None):
#         self.page_size = 5  # Set page size to 5
#         return super().paginate_queryset(queryset, request, view)
#
#     def get_paginated_response(self, data):
#         return super().get_paginated_response(data)


class VivaConfigViewSet(generics.ListAPIView):
    serializer_class_config = VivaConfigSerializer
    serializer_class_timeslot = JobVivaTimeSlotSerializer
    # pagination_class = CustomHighestFivePagination

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        config_queryset = VivaConfig.objects.filter(job_post_id=job_id)
        timeslot_queryset = JobVivaTimeSlot.objects.filter(job_post_id=job_id)
        return config_queryset, timeslot_queryset

    def list(self, request, *args, **kwargs):
        config_queryset, timeslot_queryset = self.get_queryset()

        config_page = self.paginate_queryset(config_queryset)
        config_serializer = self.serializer_class_config(config_page, many=True)

        timeslot_page = self.paginate_queryset(timeslot_queryset)
        timeslot_serializer = self.serializer_class_timeslot(timeslot_page, many=True)

        combined_data = {
            'config_data': config_serializer.data,
            'timeslot_data': timeslot_serializer.data
        }
        return self.get_paginated_response(combined_data)
#     serializer_class = VivaConfigSerializer
#     pagination_class = CustomPagination
#     def get_queryset(self):
#         job_id = self.kwargs.get('job_id')
#         return VivaConfig.objects.filter(job_post_id=job_id)
#
#
# class JobVivaTimeSlotViewSet(viewsets.ModelViewSet):
#     serializer_class = JobVivaTimeSlotSerializer
#     pagination_class = CustomPagination
#
#     def get_queryset(self):
#         job_id = self.kwargs.get('job_id')
#         return JobVivaTimeSlot.objects.filter(job_post_id=job_id)


class JobVivaTimeSlotCreateAPIView(generics.CreateAPIView):
    serializer_class = JobVivaTimeSlotSerializer