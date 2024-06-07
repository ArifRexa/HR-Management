from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from job_board.models.candidate import JobPreferenceRequest
from job_board.serializers.candidate_serializer import JobPreferenceRequestSerializer

class JobPreferenceRequestAPIView(APIView):
    def post(self, request):
        serializer = JobPreferenceRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)