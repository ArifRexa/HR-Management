# src/news_letter/serializers.py

from rest_framework import serializers
from news_letter.models.subscriber import Subscriber
from news_letter.models.segments import Segment


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ('id', 'title')
        ref_name = 'NewsletterSegment'  # Avoid naming conflicts in Swagger


class SubscriberSerializer(serializers.ModelSerializer):
    segment = SegmentSerializer(read_only=True)
    segment_id = serializers.PrimaryKeyRelatedField(
        queryset=Segment.objects.filter(is_active=True),
        source='segment',
        write_only=True,
        required=False,
        allow_null=True,
        help_text="ID of the segment to assign subscriber to"
    )

    class Meta:
        model = Subscriber
        fields = (
            'id',
            'email',
            'is_subscribed',
            'is_verified',
            'segment',
            'segment_id',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
        ref_name = 'NewsletterSubscriber'  # Important for drf-yasg schema uniqueness