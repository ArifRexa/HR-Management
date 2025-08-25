from rest_framework import serializers
from website.models import IndustryMetadata
from website.models_v2.industries_we_serve import ApplicationAreas, IndustryServe, ServeCategory

class ApplicationAreasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationAreas
        fields = ['title', 'description', 'image']

class IndustryMetadataSerializer(serializers.ModelSerializer):
    keywords = serializers.SerializerMethodField()
    class Meta:
        model = IndustryMetadata
        fields = ['title','description','canonical','keywords']

    def get_keywords(self,obj):
        return [keyword.name for keyword in obj.industrykeyword_set.all()]
    

class ServeCategorySerializer(serializers.ModelSerializer):
    # application_areas = ApplicationAreasSerializer(many=True, read_only=True)
    metadata = IndustryMetadataSerializer(many=True,source='industrymetadata_set')

    class Meta:
        model = ServeCategory
        fields = ['title', 'slug', 'metadata']

class ServeCategorySitemapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServeCategory
        fields = ['slug',]



class IndustryServeSerializer(serializers.ModelSerializer):
    serve_categories = ServeCategorySerializer(many=True, read_only=True)

    class Meta:
        model = IndustryServe
        fields = ['title', 'short_description', 'banner_image', 'motivation_title', 'motivation_description', 'serve_categories']

