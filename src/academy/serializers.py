from rest_framework import serializers

from academy.models import (
    MarketingSlider,
    Training,
    TrainingLearningTopic,
    TrainingOutline,
    TrainingProject,
    TrainingStructure,
    TrainingTechnology,
)
from website.serializers import TechnologySerializer


class MarketingSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingSlider
        fields = "__all__"


class TrainingStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingStructure
        fields = [
            "id",
            "week",
            "day",
            "description",
        ]


class TrainingOutlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingOutline
        fields = [
            "id",
            "title",
            "description",
            "image",
        ]


class TrainingTechnologySerializer(serializers.ModelSerializer):
    technology_name = TechnologySerializer(many=True)

    class Meta:
        model = TrainingTechnology
        fields = [
            "id",
            "title",
            "technology_name",
        ]


class TrainingProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingProject
        fields = [
            "id",
            "title",
            "description",
            "url",
            "image",
        ]


class TrainingLearningTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingLearningTopic
        fields = [
            "id",
            "title",
            "icon",
        ]


class TrainingSerializer(serializers.ModelSerializer):
    technology = TrainingTechnologySerializer()

    class Meta:
        model = Training
        fields = [
            "id",
            "title",
            "technology",
            "description",
            "video",
            "starts_at",
            "ends_at",
            "duration",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["training_structure"] = TrainingStructureSerializer(
            instance=instance.training_structures.all(),
            many=True,
            context={"request": self.context.get("request")},
        ).data
        data["training_outline"] = TrainingOutlineSerializer(
            instance=instance.training_outlines.all(),
            many=True,
            context={"request": self.context.get("request")},
        ).data
        data["training_project"] = TrainingProjectSerializer(
            instance=instance.training_projects.all(),
            many=True,
            context={"request": self.context.get("request")},
        ).data
        data["learning_topic"] = TrainingLearningTopicSerializer(
            instance=instance.training_learning_topics.all(),
            many=True,
            context={"request": self.context.get("request")},
        ).data
        return data


class TrainingListSerializer(serializers.ModelSerializer):
    technology = TrainingTechnologySerializer()

    class Meta:
        model = Training
        fields = [
            "id",
            "title",
            "description",
            "technology",
            "starts_at",
            "ends_at",
            "duration",
        ]
