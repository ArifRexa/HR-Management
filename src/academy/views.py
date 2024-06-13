from rest_framework.generics import ListAPIView

from academy.models import MarketingSlider
from academy.serializers import MarketingSliderSerializer

# Create your views here.

class MarketingSliderAPIListView(ListAPIView):
    serializer_class = MarketingSliderSerializer

    def get_queryset(self, *args, **kwargs):
        limit = self.request.query_params.get("limit", 6)
        return MarketingSlider.objects.all().order_by("-id")[:int(limit)]