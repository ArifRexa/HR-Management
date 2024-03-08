from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from job_board.models import VivaConfig, JobVivaTimeSlot
from job_board.serializers import VivaConfigSerializer, JobVivaTimeSlotSerializer
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from job_board.auth.CandidateAuth import CandidateAuth

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
    authentication_classes = [CandidateAuth]
    serializer_class_config = VivaConfigSerializer
    serializer_class_timeslot = JobVivaTimeSlotSerializer
    # pagination_class = CustomHighestFivePagination

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        config_queryset = VivaConfig.objects.filter(job_post_id=job_id)
        timeslot_queryset = JobVivaTimeSlot.objects.filter(job_post_id=job_id)
        return config_queryset, timeslot_queryset

    def list(self, request, *args, **kwargs):
        print('******************************')
        print(request.user)
        print(type(request.user))
        existing_slot = JobVivaTimeSlot.objects.filter(candidate=request.user).first()
        print(existing_slot)
        # if existing_slot is not None:
        #     print('return data with booked slot ')
            

        config_queryset, timeslot_queryset = self.get_queryset()

        config_page = self.paginate_queryset(config_queryset)
        config_serializer = self.serializer_class_config(config_queryset, many=True)

        timeslot_page = self.paginate_queryset(timeslot_queryset)
        timeslot_serializer = self.serializer_class_timeslot(timeslot_queryset, many=True)

        if existing_slot is not None:
            combined_data = {
            'already_booked': True,
            'start_time': existing_slot.start_time,
            'end_time': existing_slot.end_time,
            'date': existing_slot.date,
            'config_data': None,
            'booked_timeslot_data': None
        }
        else:
            combined_data = {
                'already_booked': False,
                'config_data': config_serializer.data,
                'booked_timeslot_data': timeslot_serializer.data
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
    authentication_classes = [CandidateAuth]
    serializer_class = JobVivaTimeSlotSerializer
    