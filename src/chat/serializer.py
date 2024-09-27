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


class ChildPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatPrompt
        fields = (
            "id",
            "prompt",
        )
        depth=0
    
    def __init__(self, *args, **kwargs):
        # Pass dynamic depth through kwargs or set it based on conditions
        dynamic_depth = kwargs.pop('depth_count', None)
        super().__init__(*args, **kwargs)
        
        if dynamic_depth is not None:
            self.Meta.depth = dynamic_depth


# class ChatPromptSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = ChatPrompt
#         fields = (
#             "id",
#             "prompt",
#         )



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