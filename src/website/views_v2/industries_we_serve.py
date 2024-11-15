from rest_framework import generics

from website.models_v2.industries_we_serve import IndustryServe, ServeCategory
from website.serializers_v2.industries_we_serve import IndustryServeSerializer, ServeCategorySerializer,ServeCategorySitemapSerializer

class IndustryServeListView(generics.ListAPIView):
    queryset = IndustryServe.objects.all()
    serializer_class = IndustryServeSerializer


class IndustryServeDetailView(generics.RetrieveAPIView):
    queryset = ServeCategory.objects.all()
    serializer_class = ServeCategorySerializer
    lookup_field = 'slug'


class IndustryServeSitemapListView(generics.ListAPIView):
    queryset = ServeCategory.objects.all()
    serializer_class = ServeCategorySitemapSerializer