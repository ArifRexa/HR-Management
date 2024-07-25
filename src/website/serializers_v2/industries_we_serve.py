from rest_framework import serializers
from website.models_v2.industries_we_serve import ApplicationAreas, IndustryServe, ServeCategory

class ApplicationAreasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationAreas
        fields = ['title', 'description', 'image']

class ServeCategorySerializer(serializers.ModelSerializer):
    application_areas = ApplicationAreasSerializer(many=True, read_only=True)

    class Meta:
        model = ServeCategory
        fields = ['title', 'slug', 'title_in_detail_page', 'short_description', 'industry_field_image', 'industry_banner', 'impressive_title', 'impressive_description', 'application_areas']

class IndustryServeSerializer(serializers.ModelSerializer):
    serve_categories = ServeCategorySerializer(many=True, read_only=True)

    class Meta:
        model = IndustryServe
        fields = ['title', 'short_description', 'banner_image', 'motivation_title', 'motivation_description', 'serve_categories']