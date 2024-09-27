from rest_framework import serializers

from chat.models import Chat, ChatPrompt, ChatUser


class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = (
            "id",
            "email",
            "name",
        )
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["chat"] = Chat.objects.create(client=instance).chat_id
        return data


class ChatPromptSerializer(serializers.ModelSerializer):
    childrens = serializers.SerializerMethodField()

    class Meta:
        model = ChatPrompt
        fields = ['id', 'prompt', 'childrens']

    def get_childrens(self, obj):
        # Recursively serialize the children
        if obj.childrens.exists():
            return ChatPromptSerializer(obj.childrens.all(), many=True).data
        return []