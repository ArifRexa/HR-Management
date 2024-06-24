from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from academy.models import (
    InstructorFeedback,
    MarketingSlider,
    SuccessStory,
    Training,
)
from academy.serializers import (
    InstructorFeedbackSerializer,
    MarketingSliderSerializer,
    StudentCreateSerializer,
    SuccessStorySerializer,
    TrainingListSerializer,
    TrainingSerializer,
)
from rest_framework import filters, response, permissions, parsers


class MarketingSliderAPIListView(ListAPIView):
    serializer_class = MarketingSliderSerializer

    def get_queryset(self, *args, **kwargs):
        limit = self.request.query_params.get("limit", 6)
        return MarketingSlider.objects.all().order_by("-id")[: int(limit)]


class TrainingRetrieveAPIView(RetrieveAPIView):
    serializer_class = TrainingSerializer
    queryset = Training.objects.all()


class TrainingListAPIView(ListAPIView):
    serializer_class = TrainingListSerializer
    queryset = Training.objects.all()
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ["title"]


class StudentCreateAPIView(APIView):
    serializer_class = StudentCreateSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        data = request.POST.copy()
        data.update({"file": file})
        serializer = StudentCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({"result": serializer.data})


class SuccessStoryView(ListAPIView):
    queryset = SuccessStory.objects.all()
    serializer_class = SuccessStorySerializer


class InstructorFeedbackView(ListAPIView):
    queryset = InstructorFeedback.objects.all()
    serializer_class = InstructorFeedbackSerializer
