from rest_framework.generics import ListAPIView, RetrieveAPIView

from website.models_v2.services import ServicePage
from website.serializers_v2.services import ServicePageDetailSerializer, ServicePageSerializer, ServicePageSitemapSerializer


class ServiceListView(ListAPIView):
    queryset = ServicePage.objects.filter(parent__isnull=True)
    serializer_class = ServicePageSerializer

class ServicePageSitemapListView(ListAPIView):
    queryset = ServicePage.objects.filter(parent__isnull=False)
    serializer_class = ServicePageSitemapSerializer
    pagination_class = None


class ServicePageDetailView(RetrieveAPIView):
    queryset = ServicePage.objects.all()
    serializer_class = ServicePageDetailSerializer
    # lookup_url_kwarg = "slug"
    lookup_field = "slug"
