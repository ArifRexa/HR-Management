from rest_framework import serializers

from chat.models import ChatUser


class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = (
            "id",
            "email",
            "name",
        )