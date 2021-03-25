from rest_framework import serializers

from src.job_board.models import Job


class JobsSerializer(serializers.Serializer):
    class Meta:
        model = Job
        fields = ['id', 'title']
# from rest_framework import serializers
#
# from .models import Job
#
#
# class AddJob(serializers.ModelSerializer):
#     image_url = serializers.SerializerMethodField('get_image_url')
#
#     class Meta:
#         model = Job
#         fields = ('id', 'title')
