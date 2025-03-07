from django.contrib.auth.models import User
from rest_framework import serializers

from apps.mixin.serializer import BaseModelSerializer


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")
        ref_name = "authentication_user"


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
