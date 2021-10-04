from rest_framework import serializers

from settings.models import OpenLetter


class OpenLetterSerializer(serializers.ModelSerializer):
    message = serializers.CharField(min_length=150)

    class Meta:
        model = OpenLetter
        fields = "__all__"
