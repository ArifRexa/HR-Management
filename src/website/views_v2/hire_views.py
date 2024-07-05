from rest_framework.generics import ListAPIView, RetrieveAPIView

from website.hire_models import HireResource, HireResourceContent
from website.serializers_v2.hire_serializer import (
    HireResourceContentSerializer,
    HireResourceSerializer,
)


class HireResourceListView(ListAPIView):
    queryset = HireResource.objects.all()
    serializer_class = HireResourceSerializer


class HireResourceContentDetailView(RetrieveAPIView):
    queryset = HireResourceContent.objects.all()
    serializer_class = HireResourceContentSerializer
    # lookup_url_kwarg = "slug"
    lookup_field = "slug"

    def get_object(self):
        return self.get_queryset().get(slug=self.kwargs["slug"])
