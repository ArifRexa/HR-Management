from rest_framework import serializers

from website.hire_models import (
    FAQContent,
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
)
from website.serializers import AwardSerializer, TechnologySerializer


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ["created_at", "updated_at"]


class QuoteSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Quote


class PricingSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Pricing
        exclude = ["created_at", "updated_at", "hire_resource_content"]


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
    class Meta(BaseModelSerializer.Meta):
        model = HireResourceFeatureContent
        exclude = ["created_at", "updated_at"]


class FAQContentSerializer(BaseModelSerializer):
    class Meta():
        model = FAQContent
        fields = ["question", "answer"]
        

class HireResourceFAQSerializer(BaseModelSerializer):
    faqs = FAQContentSerializer(many=True)

    class Meta:
        model = HireResourceFAQ
        fields = ["title", "sub_title", "description", "faqs"]

class HireResourceFeatureSerializer(BaseModelSerializer):
    content = HireResourceFeatureContentSerializer(many=True)

    class Meta:
        model = HireResourceFeature
        fields = ["title", "slug", "sub_title", "content"]


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
    pricings = PricingSerializer(many=True)
    service = HireServiceSerializer()
    statistic = HireResourceStatisticSerializer()
    technologies = HireResourceTechnologySerializer(many=True)
    feature = HireResourceFeatureSerializer()
    hire_process = HiringProcessSerializer()
    faq = HireResourceFAQSerializer()
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
