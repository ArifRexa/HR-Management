from rest_framework.generics import RetrieveAPIView
from website.model_v2.industry_we_serve import IndustryPage, IndustryWeServe
from website.serializers_v2.industry_we_serve import (
    IndustryPageSerializer,
    IndustryWeServeSerializer,
)


class IndustryWeServeListAPIView(RetrieveAPIView):
    serializer_class = IndustryPageSerializer
    queryset = IndustryPage.objects.all()

    def get_object(self):
        return IndustryPage.objects.first()


class IndustryWeServeRetrieveAPIViewView(RetrieveAPIView):
    serializer_class = IndustryWeServeSerializer
    queryset = IndustryWeServe.objects.all()
    lookup_field = "slug"
