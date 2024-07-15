from rest_framework import serializers

from website.csr_models import CSR,OurEffort,OurEvent


class OurEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurEvent
        fields = ('id','title', 'description', 'image')

class OurEffortSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurEffort
        fields = ('id','title', 'description', 'image')

class CSRSerializer(serializers.ModelSerializer):
    events = serializers.SerializerMethodField()
    efforts = serializers.SerializerMethodField()

    class Meta:
        model = CSR
        fields = ('id', 'title', 'short_description', 'banner_image', 'events', 'efforts')

    def get_events(self, obj):
        events = OurEvent.objects.filter(csr=obj)
        serializer = OurEventSerializer(events, many=True)
        return serializer.data

    def get_efforts(self, obj):
        efforts = OurEffort.objects.filter(csr=obj)
        serializer = OurEffortSerializer(efforts, many=True)
        return serializer.data