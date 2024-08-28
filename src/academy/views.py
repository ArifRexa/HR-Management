from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from academy.models import (
    FAQ,
    HomePageWhyBest,
    InstructorFeedback,
    MarketingSlider,
    OurAchievement,
    SuccessStory,
    Training,
    TrainingProgram
)
from academy.serializers import (
    FAQSerializer,
    InstructorFeedbackSerializer,
    MarketingSliderSerializer,
    OurAchievementSerializer,
    StudentCreateSerializer,
    SuccessStorySerializer,
    TrainingListSerializer,
    TrainingSerializer,
    WhyWeBestSerializer,
)
from rest_framework import filters, response, permissions, parsers

class OurAchievementListView(ListAPIView):
    queryset = OurAchievement.objects.all()
    serializer_class = OurAchievementSerializer

class MarketingSliderAPIListView(ListAPIView):
    serializer_class = MarketingSliderSerializer

    def get_queryset(self, *args, **kwargs):
        limit = self.request.query_params.get("limit", 6)
        return MarketingSlider.objects.all().order_by("-id")[: int(limit)]


class TrainingRetrieveAPIView(RetrieveAPIView):
    serializer_class = TrainingSerializer
    queryset = TrainingProgram.objects.all()
    lookup_field = "slug"

class FAQListView(ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    pagination_class = None


class TrainingListAPIView(ListAPIView):
    serializer_class = TrainingListSerializer
    queryset = TrainingProgram.objects.all()
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


class HomePageAPIView(ListAPIView):
    serializer_class = WhyWeBestSerializer
    queryset = HomePageWhyBest.objects.all()
