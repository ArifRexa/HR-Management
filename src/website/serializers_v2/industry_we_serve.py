from rest_framework import serializers

from website.model_v2.industry_we_serve import (
    IndustryWeServe,
    IndustryWeServeContent,
    IndustryPage,
)


class IndustryWeServeListSerializer(serializers.ModelSerializer):
    # content_list = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = IndustryWeServe
        exclude = ["created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["industry_list"] = instance.industry_we_serve_contents.values_list(
            "title", flat=True
        )

        return data


class IndustryWeServeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryWeServeContent
        exclude = ["created_at", "updated_at", "industry"]


class IndustryWeServeSerializer(serializers.ModelSerializer):
    industry_we_serve_contents = IndustryWeServeContentSerializer(many=True)

    class Meta:
        model = IndustryWeServe
        exclude = ["created_at", "updated_at", "page"]


class IndustryPageSerializer(serializers.ModelSerializer):
    industry_we_serve = IndustryWeServeListSerializer(many=True)

    class Meta:
        model = IndustryPage
        exclude = ["created_at", "updated_at"]
