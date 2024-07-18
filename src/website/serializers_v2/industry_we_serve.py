from rest_framework import serializers

from website.model_v2.industry_we_serve import (
    IndustryWeServe,
    IndustryWeServeContent,
    IndustryPage,
)


class IndustryWeServeListSerializer(serializers.ModelSerializer):
    industry_list = serializers.SerializerMethodField(read_only=True)
    
    def get_industry_list(self, obj):
        return obj.description.split("\r\n")

    class Meta:
        model = IndustryWeServe
        exclude = ["created_at", "updated_at"]

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data["industry_list"] = instance.description.split("\r\n")

    #     return data


class IndustryWeServeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryWeServeContent
        exclude = ["created_at", "updated_at", "industry"]


class IndustryWeServeSerializer(serializers.ModelSerializer):
    industry_we_serve_contents = IndustryWeServeContentSerializer(many=True)

    class Meta:
        model = IndustryWeServe
        exclude = ["created_at", "updated_at", "page"]


class IndustryPageListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    def get_children(self, obj):
        children = obj.children.all()
        
        return IndustryPageListSerializer(children, many=True, context={"request": self.context.get("request")}).data

    class Meta:
        model = IndustryPage
        exclude = ["created_at", "updated_at", "parent"]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["industry_list"] = instance.industry_we_serve.values_list("title", flat=True)

        return data


# industry_we_serve = IndustryWeServeListSerializer(many=True)


class IndustryPageDetailsSerializer(serializers.ModelSerializer):
    
    industry_we_serve = IndustryWeServeListSerializer(many=True)

    class Meta:
        model = IndustryPage
        exclude = ["created_at", "updated_at", "parent"]