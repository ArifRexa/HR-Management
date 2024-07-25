import re
from rest_framework import serializers

from website.csr_models import CSR,OurEffort,OurEvent


class OurEventSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = OurEvent
        fields = ('id', 'title', 'description', 'image')

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class OurEffortSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = OurEffort
        fields = ('id', 'title', 'description', 'image')

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
class CSRSerializer(serializers.ModelSerializer):
    events = serializers.SerializerMethodField()
    efforts = serializers.SerializerMethodField()

    class Meta:
        model = CSR
        fields = ('id', 'title', 'short_description', 'banner_image', 'events', 'efforts')

    def get_events(self, obj):
            events = OurEvent.objects.filter(csr=obj)
            serializer = OurEventSerializer(events, many=True, context=self.context)
            return serializer.data

    def get_efforts(self, obj):
            efforts = OurEffort.objects.filter(csr=obj)
            serializer = OurEffortSerializer(efforts, many=True, context=self.context)
            return serializer.data