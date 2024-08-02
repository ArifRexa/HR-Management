from rest_framework.generics import ListAPIView, RetrieveAPIView

from website.models_v2.services import ServicePage
from website.serializers_v2.services import ServicePageDetailSerializer, ServicePageSerializer


class ServiceListView(ListAPIView):
    queryset = ServicePage.objects.filter(parent__isnull=True)
    serializer_class = ServicePageSerializer


class ServicePageDetailView(RetrieveAPIView):
    queryset = ServicePage.objects.all()
    serializer_class = ServicePageDetailSerializer
    # lookup_url_kwarg = "slug"
    lookup_field = "slug"
