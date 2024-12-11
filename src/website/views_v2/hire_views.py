from rest_framework.generics import ListAPIView, RetrieveAPIView

from website.hire_models import HireResource
from website.serializers_v2.hire_serializer import (
    HireResourcePageListSerializer,
    HireResourcePageSerializer,
    HireResourcePageSitemapSerializer,
    HireResourceSerializer,
)
from website.models_v2.hire_resources import HireResourcePage


class HireResourcePageListView(ListAPIView):
    queryset = HireResourcePage.objects.filter(parents__isnull=True)
    serializer_class = HireResourcePageListSerializer
    pagination_class = None

class HireResourcePageSitemapView(ListAPIView):
    queryset = HireResourcePage.objects.filter(parents__isnull=False)
    serializer_class = HireResourcePageSitemapSerializer
    pagination_class = None
    


class HireResourceListView(ListAPIView):
    queryset = HireResource.objects.all()
    serializer_class = HireResourceSerializer


class HireResourcePageDetailView(RetrieveAPIView):
    queryset = HireResourcePage.objects.all()
    serializer_class = HireResourcePageSerializer
    # lookup_url_kwarg = "slug"
    lookup_field = "slug"
