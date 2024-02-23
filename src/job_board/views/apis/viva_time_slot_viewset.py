from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from job_board.models import VivaConfig, JobVivaTimeSlot
from job_board.serializers import VivaConfigSerializer, JobVivaTimeSlotSerializer

class VivaConfigViewSet(viewsets.ModelViewSet):
    queryset = VivaConfig.objects.all()
    serializer_class = VivaConfigSerializer

class JobVivaTimeSlotViewSet(viewsets.ModelViewSet):
    queryset = JobVivaTimeSlot.objects.all()
    serializer_class = JobVivaTimeSlotSerializer

# class BookedTimeSlotList(APIView):
#     def get(self, request, format=None):
#         # Retrieve booked time slots
#         booked_time_slots = JobVivaTimeSlot.objects.exclude(candidate=None)
#
#         # Serialize the data
#         serializer = BookedTimeSlotSerializer(booked_time_slots, many=True)
#         return Response(serializer.data)


# class BookedTimeSlotAPIView(APIView):
#     def get(self, request):
#         # Retrieve all instances of JobVivaTimeSlot
#         booked_slots = JobVivaTimeSlot.objects.all()
#
#         # Serialize the queryset
#         serializer = BookedTimeSlotSerializer(booked_slots, many=True)
#
#         # Return the serialized data
#         return Response(serializer.data)

class VivaConfigWithBookedSlotsAPIView(APIView):
    def get(self, request):
        viva_configs = VivaConfig.objects.all()
        serialized_data = VivaConfigSerializer(viva_configs, many=True).data
        return Response(serialized_data)
