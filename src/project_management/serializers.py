from rest_framework import serializers
from django.contrib.auth import get_user_model

from website.models import ProjectKeyword, ProjectMetadata
from website.models_v2.industries_we_serve import ServeCategory
from website.models_v2.services import ServicePage
from .models import (
    Project, ProjectKeyPoint, ProjectContent
)

class ProjectKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectKeyword
        fields = '__all__'
        ref_name = 'ProjectKeywordReadOnly'

class ProjectMetadataSerializer(serializers.ModelSerializer):
    # keywords = ProjectKeywordSerializer(many=True, source='projectkeyword_set', read_only=True)
    
    class Meta:
        model = ProjectMetadata
        fields = '__all__'
        ref_name = 'ProjectMetadataReadOnly'

class ProjectKeyPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectKeyPoint
        fields = '__all__'
        ref_name = 'ProjectKeyPointReadOnly'

class ProjectContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectContent
        fields = '__all__'
        ref_name = 'ProjectContentReadOnly'

class ProjectDetailSerializer(serializers.ModelSerializer):
    key_points = ProjectKeyPointSerializer(many=True, source='projectkeypoint_set', read_only=True)
    contents = ProjectContentSerializer(many=True, source='projectcontent_set', read_only=True)
    metadata = ProjectMetadataSerializer(source='project_metadata', many=True, read_only=True)  # ✅
    
    class Meta:
        model = Project
        # fields = '__all__'
        exclude = ['created_by']
        depth = 1
        ref_name = 'ProjectDetailReadOnly'


# class ProjectListSerializer(serializers.ModelSerializer):
#     """Lightweight serializer for project list"""
#     client_name = serializers.CharField(source='client.name', read_only=True)
#     client_image = serializers.ImageField(source='client.image', read_only=True)
    
#     class Meta:
#         model = Project
#         fields = [
#             'id', 'title', 'slug', 'description', 'client_name', 
#             'client_image', 'featured_image', 'thumbnail', 'live_link', 'industries', 'services', 'technology',
#             'active', 'show_in_website', 'created_at', 'updated_at'
#         ]
#         ref_name = 'ProjectListReadOnly'

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServeCategory
        fields = ['id', 'title', 'slug']
        ref_name = 'ProjectIndustryReadOnly'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePage
        fields = ['id', 'title', 'slug', 'h1_title', 'sub_title', 'description']
        ref_name = 'ProjectServiceReadOnly'

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        from website.models import Technology
        model = Technology
        fields = ['id', 'name', 'slug', 'type', 'icon']
        ref_name = 'ProjectTechnologyReadOnly'

class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for project list"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_image = serializers.ImageField(source='client.image', read_only=True)
    industries = IndustrySerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    technology = TechnologySerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'client_name', 
            'client_image', 'client_review', 'client_designation', 'featured_image', 'thumbnail', 'live_link', 'project_logo',
            'industries', 'services', 'technology',
            'active', 'show_in_website', 'is_special', 'created_at', 'updated_at'
        ]
        
        ref_name = 'ProjectListReadOnly'









# class ProjectKeywordSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProjectKeyword
#         fields = '__all__'
#         ref_name = 'ProjectKeywordReadOnly'

# class ProjectMetadataSerializer(serializers.ModelSerializer):
#     keywords = ProjectKeywordSerializer(many=True, source='projectkeyword_set', read_only=True)
    
#     class Meta:
#         model = ProjectMetadata
#         fields = '__all__'
#         ref_name = 'ProjectMetadataReadOnly'

# class ProjectKeyPointSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProjectKeyPoint
#         fields = '__all__'
#         ref_name = 'ProjectKeyPointReadOnly'

# class ProjectContentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProjectContent
#         fields = '__all__'
#         ref_name = 'ProjectContentReadOnly'

# class UserSerializer(serializers.ModelSerializer):
#     """Lightweight user serializer without groups and permissions"""
#     class Meta:
#         model = get_user_model()
#         fields = ['id', 'username', 'first_name', 'last_name', 'email']
#         ref_name = 'ProjectUserReadOnly'

# class ProjectListSerializer(serializers.ModelSerializer):
#     """Lightweight serializer for project list"""
#     client_name = serializers.CharField(source='client.name', read_only=True)
#     client_image = serializers.ImageField(source='client.image', read_only=True)
#     created_by = UserSerializer(read_only=True)
    
#     class Meta:
#         model = Project
#         fields = [
#             'id', 'title', 'slug', 'description', 'client_name', 
#             'client_image', 'featured_image', 'thumbnail', 'live_link',
#             'active', 'show_in_website', 'created_at', 'updated_at', 'created_by'
#         ]
#         ref_name = 'ProjectListReadOnly'

# class ProjectDetailSerializer(serializers.ModelSerializer):
#     """Detailed serializer with all nested data"""
#     key_points = ProjectKeyPointSerializer(many=True, source='projectkeypoint_set', read_only=True)
#     contents = ProjectContentSerializer(many=True, source='projectcontent_set', read_only=True)
#     metadata = serializers.SerializerMethodField()
#     client_details = serializers.SerializerMethodField()
#     created_by = UserSerializer(read_only=True)
#     updated_by = UserSerializer(read_only=True)
    
#     class Meta:
#         model = Project
#         fields = '__all__'
#         ref_name = 'ProjectDetailReadOnly'
    
#     def get_metadata(self, obj):
#         """Manually fetch metadata to avoid relation issues"""
#         try:
#             metadata = obj.projectmetadata
#             return ProjectMetadataSerializer(metadata).data
#         except AttributeError:
#             try:
#                 metadata = obj.projectmetadata_set.first()
#                 return ProjectMetadataSerializer(metadata).data if metadata else None
#             except AttributeError:
#                 return None
    
#     def get_client_details(self, obj):
#         if obj.client:
#             return {
#                 'id': obj.client.id,
#                 'name': obj.client.name,
#                 'company_name': obj.client.company_name,
#                 'logo': obj.client.logo.url if obj.client.logo else None,
#                 'image': obj.client.image.url if obj.client.image else None,
#             }
#         return None