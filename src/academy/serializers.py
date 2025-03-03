from rest_framework import serializers

from academy.models import (
    HomeBanner,
    HomePageWhyBest,
    InstructorFeedback,
    MarketingSlider,
    PageBanner,
    Student,
    SuccessStory,
    Training,
    TrainingLearningTopic,
    TrainingOutline,
    TrainingProject,
    TrainingStructure,
    TrainingStructureModule,
    TrainingTechnology,
    OurAchievement,
    FAQ,
    TrainingProgram, PracticeProject, FeatureHighlight, TrainingReason, TrainingFor, 
    Training_Outline, ProjectShowcase, StudentReview, TrainingFAQ,Instructor
)
from website.serializers import TechnologySerializer
from project_management.models import Technology

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("question", "answer")
        ref_name = "academy_faq"


class OurAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurAchievement
        fields = ("title", "number", "icon")
        ref_name = "academy_our_achievement"

class MarketingSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingSlider
        fields = "__all__"
        ref_name = "academy_marketing_slider"


class TrainingStructureModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingStructureModule
        fields = [
            "description",
        ]
        ref_name = "academy_training_structure_module"




class TrainingStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingStructure
        fields = [
            "week",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["days"] = TrainingStructureModuleSerializer(
            instance=instance.training_modules.filter(
                training=self.context.get("training"), training_structure=instance
            ),
            many=True,
            context={"request": self.context.get("request")},
        ).data
        return data


class TrainingOutlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingOutline
        fields = [
            "title",
            "description",
            "image",
        ]


# class TrainingTechnologySerializer(serializers.ModelSerializer):
#     technology_name = TechnologySerializer(many=True)

#     class Meta:
#         model = TrainingTechnology
#         fields = [
#             "title",
#             "technology_name",
#         ]


class TrainingProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingProject
        fields = [
            "image",
        ]


class TrainingLearningTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingLearningTopic
        fields = [
            "title",
            "icon",
        ]


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'image', 'designation', 'rating', 'short_description', 'thumbnail', 'video']

class PracticeProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeProject
        fields = ['id', 'slug', 'title','image', 'short_description', 'description']

class TrainingReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingReason
        fields = ['id', 'title', 'image']

class TrainingForSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingFor
        fields = ['id', 'icon', 'prospect', 'description']

class Training_OutlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training_Outline
        fields = ['id', 'title', 'duration', 'description']

class ProjectShowcaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectShowcase
        fields = ['id', 'title', 'video', 'thumbnail']

class StudentReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentReview
        fields = ['id', 'title', 'video', 'thumbnail']

class TrainingFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingFAQ
        fields = ['id', 'question', 'answer']

class TrainingTechnologySerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Technology  # Assuming you have a Technology model
        fields = ['id', 'name', 'icon']  # Add relevant fields for technology

    def get_icon(self, obj):
        request = self.context.get('request')
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        return None


class FeatureHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureHighlight
        fields = ['id', 'image']
class PracticeProjectDetailsSerializer(serializers.ModelSerializer):
    feature_highlights = FeatureHighlightSerializer(many=True, source='featurehighlight_set')
    training_technology = serializers.SerializerMethodField()
    training_tools_title = serializers.SerializerMethodField()
    training_tools_subtitle = serializers.SerializerMethodField()

    class Meta:
        model = PracticeProject
        fields = [
            'id', 'slug', 'title', 'short_description', 'description', 
            'feature_highlights', 'training_technology',
            'training_tools_title', 'training_tools_subtitle'
        ]

    def get_training_technology(self, obj):
        request = self.context.get('request')
        training_programs = TrainingProgram.objects.filter(practice_projects=obj)
        technologies = Technology.objects.filter(trainingprogram__in=training_programs).distinct()
        return TrainingTechnologySerializer(technologies, many=True ,context={'request': request}).data

    def get_training_tools_title(self, obj):
        training_program = TrainingProgram.objects.filter(practice_projects=obj).first()
        return training_program.training_tools_title if training_program else None

    def get_training_tools_subtitle(self, obj):
        training_program = TrainingProgram.objects.filter(practice_projects=obj).first()
        return training_program.training_tools_subtitle if training_program else None

class TrainingProgramDetailSerializer(serializers.ModelSerializer):
    instructors = InstructorSerializer(many=True)
    practice_projects = PracticeProjectSerializer(many=True)
    training_reasons = TrainingReasonSerializer(many=True)
    training_for = TrainingForSerializer(many=True)
    trainingoutline = Training_OutlineSerializer(many=True)
    project_showcase = ProjectShowcaseSerializer(many=True)
    student_review = StudentReviewSerializer(many=True)
    training_faq = TrainingFAQSerializer(many=True)
    training_technology = TrainingTechnologySerializer(many=True)
    
    class Meta:
        model = TrainingProgram
        fields = [
            'id', 'slug', 'title', 'description', 'course_fee', 'video', 'image',
            'instructors', 'course_overview_subtitle', 'course_overview_image', 
            'course_overview_description', 'training_reason_title', 
            'training_for_title', 'training_for_subtitle', 'training_outline_title', 
            'training_outline_subtitle', 'training_tools_title', 'training_tools_subtitle', 
            'training_technology', 'project_title', 'project_subtitle', 
            'practice_projects', 'project_showcase_title', 
            'project_showcase_description', 'student_review_title', 
            'student_review_description', 'training_faq_subtitle',
            'training_reasons', 'training_for', 'trainingoutline', 
            'project_showcase', 'student_review', 'training_faq'
        ]


class TrainingListSerializer(serializers.ModelSerializer):
    training_technology = TechnologySerializer(many=True, read_only=True)
    class Meta:
        model = TrainingProgram
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "image",
            "training_technology",
            "program_active_status",
            
        ]

    

class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "name",
            "email",
            "phone",
            "details",
            "training",
            "image",
            "file",
        ]


class SuccessStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessStory
        fields = "__all__"


class InstructorFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorFeedback
        exclude = ["created_at", "updated_at"]


class WhyWeBestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePageWhyBest
        exclude = ["created_at", "updated_at"]

class HomePageSerializer(serializers.Serializer):
    why_we_best = WhyWeBestSerializer(many=True)
    
    
class BaseBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        exclude = ['id', 'created_at', 'updated_at', 'page_banner']
        

class PageBannerSerializer(serializers.ModelSerializer):
    home = BaseBannerSerializer(source="homebanner", read_only=True)
    all_training = BaseBannerSerializer(source="alltrainingbanner", read_only=True)
    instructor = BaseBannerSerializer(source="instructorbanner", read_only=True)
    success_story = BaseBannerSerializer(source="successstorybanner", read_only=True)
    
    class Meta:
        model = PageBanner
        exclude = ['id', 'created_at', 'updated_at']
        ref_name = "academy_page_banner"
