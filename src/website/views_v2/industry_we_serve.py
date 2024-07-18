from rest_framework.generics import RetrieveAPIView, ListAPIView
from website.model_v2.industry_we_serve import IndustryPage, IndustryWeServe
from website.serializers_v2.industry_we_serve import (
    IndustryPageListSerializer,
    IndustryPageDetailsSerializer,
)


class IndustryWeServeListAPIView(RetrieveAPIView):
    serializer_class = IndustryPageListSerializer
    queryset = IndustryPage.objects.all()

    def get_object(self):
        return IndustryPage.objects.filter(parent__isnull=True).first()


class IndustryWeServeRetrieveAPIViewView(RetrieveAPIView):
    serializer_class = IndustryPageDetailsSerializer
    queryset = IndustryPage.objects.all()
    lookup_field = "slug"
