from rest_framework import serializers
from website.models_v2.woman_empowermens import WomanEmpowerment, WomanAchievement, WomanInspiration, Environment, Photo

class WomanAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = WomanAchievement
        fields = '__all__'

class WomanInspirationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WomanInspiration
        fields = '__all__'

class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = '__all__'

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'

class WomanEmpowermentSerializer(serializers.ModelSerializer):
    achievements = WomanAchievementSerializer(many=True, read_only=True)
    inspirations = WomanInspirationSerializer(many=True, read_only=True)
    environments = EnvironmentSerializer(many=True, read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = WomanEmpowerment
        fields = '__all__'