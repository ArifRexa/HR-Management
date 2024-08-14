from rest_framework import serializers
from website.models_v2.services import (
    ServicePage,
    ServiceFAQQuestion,
    DevelopmentServiceProcess,
    DiscoverOurService,
    ComparativeAnalysis,
)


class ServicePageChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePage
        fields = (
            "title",
            "sub_title",
            "menu_title",
            "slug",
        )


class ServicePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePage
        fields = (
            "title",
            "sub_title",
            "menu_title",
            "banner_query",
            "feature_image",
            "icon",
            "slug",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["children"] = ServicePageChildSerializer(
            instance.children.all(), many=True, context=self.context
        ).data
        return data


class BaseServicePageSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ("id", "services", "created_at", "updated_at")


class DevelopmentServiceProcessSerializer(BaseServicePageSerializer):
    class Meta(BaseServicePageSerializer.Meta):
        model = DevelopmentServiceProcess


class DiscoverOurServiceSerializer(BaseServicePageSerializer):
    class Meta(BaseServicePageSerializer.Meta):
        model = DiscoverOurService


class ComparativeAnalysisSerializer(BaseServicePageSerializer):
    class Meta(BaseServicePageSerializer.Meta):
        model = ComparativeAnalysis

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["criteria"] = instance.criteria.title
        return data


class ServiceFAQQuestionSerializer(BaseServicePageSerializer):
    class Meta:
        model = ServiceFAQQuestion
        exclude = ("id",)


class ServicePageDetailSerializer(serializers.ModelSerializer):
    development_services_process = DevelopmentServiceProcessSerializer(many=True)
    discover_services = DiscoverOurServiceSerializer(many=True)
    comparative_analysis = ComparativeAnalysisSerializer(many=True)
    questions = ServiceFAQQuestionSerializer(many=True)

    class Meta:
        model = ServicePage
        exclude = ("is_parent", "parent", "created_at", "updated_at")
