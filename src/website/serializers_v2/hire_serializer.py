from rest_framework import serializers

from website.hire_models import (
    FAQContent,
    HireEngagement,
    HireEngagementContent,
    HirePricing,
    HireResource,
    HireResourceContent,
    HireResourceFAQ,
    HireResourceFeature,
    HireResourceFeatureContent,
    HireResourceStatistic,
    HireResourceStatisticContent,
    HireResourceTechnology,
    HireService,
    HireServiceContent,
    HiringProcess,
    HiringProcessContent,
    Pricing,
    Quote,
    HirePageStaticContent,
)
from website.serializers import AwardSerializer, TechnologySerializer


from website.models_v2.hire_resources import (
    HireResourcePage,
    HireResourceService,
    DeveloperPriceType,
    FAQQuestion,
    HireResourceServiceContent,
    HiringStep,
    Cost,
    Criteria,
    CostType,
)
from website.models import HireResourceMetadata

class HireResourceChildrenSerializer(serializers.ModelSerializer):
    class Meta:
        model = HireResourcePage
        fields = [
            "title",
            "slug",
        ]



class HireResourcePageSitemapSerializer(serializers.ModelSerializer):
    child_slug = serializers.CharField(source="slug")
    class Meta:
        model = HireResourcePage
        fields = [
            "child_slug",
            # "updated_at"
        ]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["parent_slug"] = instance.parents.slug
        data["slug"] = f"{instance.parents.slug}/{instance.slug}"
        return data

class HireResourcePageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HireResourcePage
        fields = [
            "title",
            "sub_title",
            "slug",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["children"] = HireResourceChildrenSerializer(
            instance.children.all(), many=True, context=self.context
        ).data
        return data


class CriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criteria
        fields = ["title"]


class CostTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostType
        fields = ["title"]


class CostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cost
        exclude = ["hire_resource"]


class HiringStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringStep
        exclude = ["hiring_process"]


class DeveloperPriceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeveloperPriceType
        exclude = ["hire_resource"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["criteria"] = instance.criteria.title
        return data


class FAQQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQQuestion
        fields = ["question", "answer"]


class HireResourceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HireResourceService
        fields = ["title", "short_description", "description"]


class HireResourceMetadataSerializer(serializers.ModelSerializer):
    keywords = serializers.SerializerMethodField()
    class Meta:
        model = HireResourceMetadata
        fields = ('title','description','canonical','keywords')

    def get_keywords(self,obj):
        return [keyword.name for keyword in obj.hireresourcekeyword_set.all()]


class HireResourceServiceContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HireResourceServiceContent
        fields = '__all__'

class HireResourcePageSerializer(serializers.ModelSerializer):
    hire_resource_service_content = HireResourceServiceContentSerializer(many=True, source='hire_resource')
    costs = CostSerializer(many=True)
    developer_price_types = DeveloperPriceTypeSerializer(many=True)
    services = HireResourceServiceSerializer(many=True)
    metadata = HireResourceMetadataSerializer(many=True,source='hireresourcemetadata_set')
    class Meta:
        model = HireResourcePage
        exclude = ["parents", "is_parent"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["faq_questions"] = FAQQuestionSerializer(
            instance.questions.all(), many=True, context=self.context
        ).data
        data["hiring_steps"] = HiringStepSerializer(
            instance.steps.all(), many=True, context=self.context
        ).data
        return data


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ["created_at", "updated_at"]


class HireEngagementContentSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = HireEngagementContent
        exclude = ["created_at", "updated_at"]


class HireEngagementSerializer(BaseModelSerializer):
    content = HireEngagementContentSerializer(many=True)

    class Meta(BaseModelSerializer.Meta):
        model = HireEngagement
        exclude = ["created_at", "updated_at"]


class HirePageStaticContentSerializer(BaseModelSerializer):
    class Meta:
        model = HirePageStaticContent
        fields = ["title", "description", "icon"]


class QuoteSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Quote


class PricingSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Pricing
        exclude = ["created_at", "updated_at"]


class HirePricingSerializer(BaseModelSerializer):
    pricing_content = PricingSerializer(many=True)

    class Meta(BaseModelSerializer.Meta):
        model = HirePricing
        exclude = ["created_at", "updated_at"]


class HireServiceContentSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = HireServiceContent
        exclude = ["created_at", "updated_at"]


class HireServiceSerializer(BaseModelSerializer):
    content = HireServiceContentSerializer(many=True)

    class Meta:
        model = HireService
        fields = ["title", "image", "content"]


class HireResourceStatisticContentSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = HireResourceStatisticContent
        exclude = ["created_at", "updated_at"]


class HireResourceStatisticSerializer(BaseModelSerializer):
    content = HireResourceStatisticContentSerializer(many=True)

    class Meta:
        model = HireResourceStatistic
        fields = ["title", "slug", "sub_title", "content"]


class HireResourceTechnologySerializer(BaseModelSerializer):
    technologies = TechnologySerializer(many=True)

    class Meta:
        model = HireResourceTechnology
        fields = ["title", "technologies"]


class HireResourceFeatureContentSerializer(BaseModelSerializer):
    class Meta:
        model = HireResourceFeatureContent
        fields = ["title", "description"]


class FAQContentSerializer(BaseModelSerializer):
    class Meta:
        model = FAQContent
        fields = ["question", "answer"]


class HireResourceFAQSerializer(BaseModelSerializer):
    faqs = FAQContentSerializer(many=True)

    class Meta:
        model = HireResourceFAQ
        fields = ["title", "sub_title", "description", "faqs"]


class HireResourceFeatureSerializer(BaseModelSerializer):
    feature_contents = HireResourceFeatureContentSerializer(many=True)

    class Meta:
        model = HireResourceFeature
        fields = ["title", "slug", "sub_title", "feature_contents"]


class HiringProcessContentSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = HiringProcessContent
        exclude = ["created_at", "updated_at"]


class HiringProcessSerializer(BaseModelSerializer):
    content = HiringProcessContentSerializer(many=True)

    class Meta:
        model = HiringProcess
        fields = ["title", "sub_title", "content"]


class HireResourceContentSerializer(BaseModelSerializer):
    awards = AwardSerializer(many=True)
    quote = QuoteSerializer()
    pricing = HirePricingSerializer()
    service = HireServiceSerializer()
    statistic = HireResourceStatisticSerializer()
    technologies = HireResourceTechnologySerializer(many=True)
    feature = HireResourceFeatureSerializer()
    hire_process = HiringProcessSerializer()
    engagement = HireEngagementSerializer()
    faq = HireResourceFAQSerializer()
    world_class_talent = HirePageStaticContentSerializer(many=True)
    on_demand_team = HirePageStaticContentSerializer(many=True)

    class Meta(BaseModelSerializer.Meta):
        model = HireResourceContent
        exclude = ["created_at", "updated_at", "resource"]


class HireResourceContentListSerializer(BaseModelSerializer):
    class Meta:
        model = HireResourceContent
        fields = ["title", "slug", "sub_title"]


class HireResourceSerializer(BaseModelSerializer):
    hire_resource_contents = HireResourceContentListSerializer(many=True)

    class Meta(BaseModelSerializer.Meta):
        model = HireResource
