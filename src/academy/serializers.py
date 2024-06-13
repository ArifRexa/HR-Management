from rest_framework import serializers

from academy.models import MarketingSlider


class MarketingSliderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MarketingSlider
        fields = '__all__'