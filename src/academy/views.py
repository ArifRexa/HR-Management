from rest_framework.generics import ListAPIView, RetrieveAPIView

from academy.models import MarketingSlider, Training
from academy.serializers import (
    MarketingSliderSerializer,
    TrainingListSerializer,
    TrainingSerializer,
)
from rest_framework import filters
# Create your views here.


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
