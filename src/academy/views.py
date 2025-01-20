from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from academy.models import (
    FAQ,
    HomePageWhyBest,
    InstructorFeedback,
    MarketingSlider,
    OurAchievement,
    PageBanner,
    SuccessStory,
    Training,
    TrainingProgram,PracticeProject,
    
)
from academy.serializers import (
    FAQSerializer,
    InstructorFeedbackSerializer,
    MarketingSliderSerializer,
    OurAchievementSerializer,
    PageBannerSerializer,
    StudentCreateSerializer,
    SuccessStorySerializer,
    TrainingListSerializer,
    TrainingProgramDetailSerializer,
    WhyWeBestSerializer,PracticeProjectDetailsSerializer
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
    serializer_class = TrainingProgramDetailSerializer
    queryset = TrainingProgram.objects.all()
    lookup_field = "slug"

class FAQListView(ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    pagination_class = None


class TrainingListAPIView(ListAPIView):
    serializer_class = TrainingListSerializer
    queryset = TrainingProgram.objects.filter(program_active_status='Active')
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ["title"]

from django.http import Http404
class PracticeProjectDetailView(RetrieveAPIView):
    queryset = PracticeProject.objects.all()
    serializer_class = PracticeProjectDetailsSerializer
    lookup_field = 'slug'
    
    def get_object(self):
        queryset = self.get_queryset()
        training_slug = self.kwargs.get('training_slug')
        project_slug = self.kwargs.get('project_slug')
        obj = queryset.filter(slug=project_slug, trainingprogram__slug=training_slug).first()
        if not obj:
            raise Http404("No PracticeProject matches the given query.")
        return obj

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


class PageBannerAPIView(RetrieveAPIView):
    queryset = PageBanner.objects.all()
    serializer_class = PageBannerSerializer
    
    def get_object(self):
        return PageBanner.objects.first()