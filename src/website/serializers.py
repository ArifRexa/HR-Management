# from pyexpat import model
from rest_framework import serializers

# from chat import models
from employee.models import (
    Employee,
    EmployeeContent,
    EmployeeNOC,
    EmployeeSkill,
    EmployeeSocial,
    Skill,
)
from project_management.models import (
    Client,
    ClientFeedback,
    OurTechnology,
    Project,
    ProjectContent,
    ProjectKeyFeature,
    ProjectKeyPoint,
    ProjectPlatform,
    ProjectResults,
    ProjectResultStatistic,
    ProjectScreenshot,
    ProjectServiceSolution,
    ProjectTechnology,
    Tag,
    Technology,
)
from settings.models import Designation
from website.models import (
    FAQ,
    AllServicesTitle,
    Award,
    AwardsTitle,
    BenefitsOfEmployment,
    Blog,
    BlogCategory,
    BlogComment,
    BlogContext,
    BlogFAQ,
    BlogMeatadata,
    BlogSEOEssential,
    BlogStatus,
    BlogTag,
    BlogTitle,
    Brand,
    Category,
    Contact,
    EmployeePerspective,
    EmployeeTestimonial,
    FAQHomeTitle,
    Gallery,
    HomeBanner,
    Industry,
    IndustryTitle,
    IndustryWeServe,
    Inquiry,
    Lead,
    Leadership,
    LeadershipSpeech,
    LifeAtMediusware,
    LifeAtMediuswareTitle,
    ModelTitle,
    OfficeLocation,
    OurAchievement,
    OurGrowth,
    OurJourney,
    OurJourneyTitle,
    PageBanner,
    PostCredential,
    ProjectMetadata,
    ProjectServiceSolutionTitle,
    ProjectsVideoTitle,
    Service,
    ServiceContent,
    ServiceMeatadata,
    ServiceProcess,
    SpecialProjectsTitle,
    Subscription,
    TechnologyTitle,
    TextualTestimonialTitle,
    VideoTestimonial,
    VideoTestimonialTitle,
    WebsiteTitle,
    WhyUsTitle,
)
from website.models_v2.services import ServicePage


class PostCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCredential
        fields = (
            "id",
            "name",
            "platform",
            "token",
        )


class ProjectPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlatform
        fields = ("title",)


class ProjectIndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryWeServe
        fields = ("title",)


class ProjectServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePage
        fields = ("menu_title",)


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ("icon", "name")


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "name",
            "email",
            "designation",
            "address",
            "country",
            "logo",
            "client_feedback",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["projects"] = ProjectSerializer(
            instance=instance.project_set.filter(active=True), many=True
        ).data
        return data


class OurClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("name", "designation", "logo", "client_feedback")


class ServiceTechnologySerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True)

    class Meta:
        model = ProjectTechnology
        fields = ("title", "technologies")


class ServiceProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProcess
        fields = "__all__"


class IndustrySerializer(serializers.ModelSerializer):
    technology = TechnologySerializer(many=True)

    class Meta:
        model = Industry
        fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
    technologies = ServiceTechnologySerializer(
        many=True, source="servicetechnology_set"
    )
    industry = IndustrySerializer(many=True)

    class Meta:
        model = Service
        fields = (
            "title",
            "sub_title",
            "slug",
            "short_description",
            "feature",
            "technologies",
            "industry",
            "feature_image",
        )


class ServiceContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceContent
        fields = (
            "title",
            "content",
            "image",
        )


class ServiceMetadataSerializer(serializers.ModelSerializer):
    keywords = serializers.SerializerMethodField()

    class Meta:
        model = ServiceMeatadata
        fields = ("title", "description", "canonical", "keywords")

    def get_keywords(self, obj):
        return [keyword.name for keyword in obj.servicekeyword_set.all()]


class ServiceDetailsSerializer(serializers.ModelSerializer):
    clients = ClientSerializer(many=True)
    technologies = ServiceTechnologySerializer(
        many=True, source="servicetechnology_set"
    )
    service_process = ServiceProcessSerializer(many=True)
    service_contents = ServiceContentSerializer(many=True, source="servicecontent_set")
    metadata = ServiceMetadataSerializer(many=True, source="servicemeatadata_set")

    class Meta:
        model = Service
        fields = (
            "slug",
            "title",
            "sub_title",
            "short_description",
            "banner_image",
            "feature_image",
            "feature",
            "service_process",
            "technologies",
            "service_contents",
            "clients",
            "metadata",
        )


class ProjectTechnologySerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True)

    class Meta:
        model = ProjectTechnology
        fields = ("title", "technologies")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name",)


class AvailableTagSerializer(serializers.ModelSerializer):
    tags_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ("id", "name", "tags_count")

    def get_tags_count(self, obj):
        return Project.objects.filter(tags=obj, show_in_website=True).count()


class ClientFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientFeedback
        fields = ("feedback",)


class ProjectScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectScreenshot
        fields = ("image",)


class ProjectClientFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientFeedback
        fields = (
            # "feedback_week",
            "feedback",
            "avg_rating",
            "rating_communication",
            # "rating_output",
            "rating_time_management",
            # "rating_billing",
            "rating_long_term_interest",
        )


class ProjectKeyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectKeyFeature
        fields = ("title", "description", "img", "img2")


class ProjectResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectResults
        fields = (
            "title",
            "increased_sales",
            "return_on_investment",
            "increased_order_rate",
        )


class ProjectResultStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectResultStatistic
        fields = (
            "title",
            "result",
        )


class ProjectSerializer(serializers.ModelSerializer):
    technologies = ProjectTechnologySerializer(
        many=True, source="projecttechnology_set"
    )
    project_results = ProjectResultStatisticsSerializer(many=True)
    platforms = ProjectPlatformSerializer(many=True)
    industries = ProjectIndustrySerializer()
    services = ProjectServiceSerializer()
    title = serializers.SerializerMethodField()
    service_solution_title = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "title",
            "slug",
            "description",
            "industries",
            "services",
            "platforms",
            "featured_image",
            "display_image",
            "project_results",
            "technologies",
            "service_solution_title",
            "project_logo",
        )

    def get_title(self, obj):
        return obj.web_title if obj.web_title else obj.title

    # def get_industries(self, obj):
    #     return [industry.title for industry in obj.industries.all()]

    def get_service_solution_title(self, obj):
        if not obj:
            return []
        return [obj.title for obj in obj.service_solutions.all()]

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['service_solution_title'] = [item.title for item in instance.service_solutions.all()]
    #     return data


class ProjectSitemapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("slug", "updated_at")


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("description", "thumbnail", "featured_video")


class ProjectServiceSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectServiceSolution
        fields = (
            "title",
            "short_description",
            "description",
        )


class ProjectContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectContent
        fields = ("title", "content", "image", "image2")


class ProjectMetadataSerializer(serializers.ModelSerializer):
    keywords = serializers.SerializerMethodField()

    class Meta:
        model = ProjectMetadata
        fields = ("title", "description", "canonical", "keywords")

    def get_keywords(self, obj):
        return [keyword.name for keyword in obj.projectkeyword_set.all()]


class ProjectDetailsSerializer(serializers.ModelSerializer):
    technologies = ProjectTechnologySerializer(
        many=True, source="projecttechnology_set"
    )
    # available_tags = TagSerializer(read_only=True, many=True, source="tags")
    client = ClientSerializer()
    # client_feedback = ProjectClientFeedbackSerializer(
    #     many=True, source="clientfeedback_set"
    # )
    project_design = ProjectScreenshotSerializer(
        source="projectscreenshot_set", many=True, read_only=True
    )
    project_contents = ProjectContentSerializer(many=True, source="projectcontent_set")
    project_key_feature = ProjectKeyFeatureSerializer(
        many=True, source="projectkeyfeature_set"
    )
    project_results = ProjectResultStatisticsSerializer(many=True)
    platforms = ProjectPlatformSerializer(many=True)
    industries = ProjectIndustrySerializer()
    services = ProjectServiceSerializer()
    service_solutions = ProjectServiceSolutionSerializer(many=True)
    country = serializers.SerializerMethodField()
    metadata = ProjectMetadataSerializer(many=True, source="projectmetadata_set")

    class Meta:
        model = Project
        fields = (
            "title",
            "slug",
            "platforms",
            "web_title",
            "industries",
            "live_link",
            "country",
            "services",
            "client_web_name",
            "client_image",
            "client_review",
            "project_logo",
            # "location_image",
            # "service_we_provide_image",
            # "industry_image",
            "project_results",
            "description",
            "featured_image",
            "featured_video",
            "technologies",
            # "available_tags",
            "project_contents",
            "project_key_feature",
            "client",
            # "client_feedback",
            "project_design",
            "service_solutions",
            "metadata",
        )

    def get_country(self, obj):
        if not obj.country:
            return None
        return obj.country.name

    def to_representation(self, instance):
        request = self.context.get("request")
        data = super().to_representation(instance)
        data["platform_image"] = [
            request.build_absolute_uri(obj.image.url)
            for obj in instance.platformimage_set.all()
        ]
        return data


class ProjectKeyPointSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectKeyPoint
        fields = ["title", "icon_url"]

    def get_icon_url(self, obj):
        request = self.context.get("request")
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        return None


class SpecialProjectSerializer(serializers.ModelSerializer):
    project_logo_url = serializers.SerializerMethodField()
    project_key_points = ProjectKeyPointSerializer(
        source="projectkeypoint_set", many=True
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "slug",
            "description",
            "project_logo_url",
            "special_image",
            "project_key_points",
        ]

    def get_project_logo_url(self, obj):
        request = self.context.get("request")
        if obj.project_logo and request:
            return request.build_absolute_uri(obj.project_logo.url)
        return None


class ProjectHighlightedSerializer(serializers.ModelSerializer):
    project_results = ProjectResultsSerializer()
    technologies = ProjectTechnologySerializer(
        many=True, source="projecttechnology_set"
    )

    class Meta:
        model = Project
        fields = (
            "slug",
            "title",
            "description",
            "project_results",
            "thumbnail",
            "technologies",
        )


class EmployeeSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSocial
        fields = ("title", "url")


class EmployeeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeContent
        fields = ("title", "content")


class EmployeeSerializer(serializers.ModelSerializer):
    designation = serializers.StringRelatedField(many=False)
    socials = EmployeeSocialSerializer(
        many=True, read_only=True, source="employeesocial_set"
    )

    class Meta:
        model = Employee
        fields = ("slug", "full_name", "designation", "manager", "image", "socials")
        ref_name = "website_employee"

    def get_image_url(self, employee):
        request = self.context.get("request")
        image_url = employee.image.url
        return request.build_absolute_uri(image_url)


class EmployeeDetailsSerializer(serializers.ModelSerializer):
    designation = serializers.StringRelatedField(many=False)
    socials = EmployeeSocialSerializer(
        many=True, read_only=True, source="employeesocial_set"
    )
    contents = EmployeeContentSerializer(
        many=True, read_only=True, source="employeecontent_set"
    )

    class Meta:
        model = Employee
        fields = (
            "slug",
            "full_name",
            "joining_date",
            "permanent_date",
            "designation",
            "manager",
            "image",
            "socials",
            "contents",
        )


class DesignationSetSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Designation
        fields = ["id", "title", "employee_count"]

    def get_employee_count(self, obj):
        return Employee.objects.filter(
            designation=obj, active=True, show_in_web=True
        ).count()


# class EmployeeSkillSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EmployeeSkill
#         fields = ['employee']


class SkillSerializer(serializers.ModelSerializer):
    total_employees = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ["id", "title", "total_employees"]

    def get_total_employees(self, obj):
        return Employee.objects.filter(
            employeeskill__skill=obj, active=True, show_in_web=True
        ).count()


class EmployeeSerializer(serializers.ModelSerializer):
    designation = serializers.SerializerMethodField()
    employeeskill = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "slug",
            "full_name",
            "designation",
            "image",
            "operation",
            "employeeskill",
        ]

    def get_designation(self, obj):
        if obj.designation:
            return obj.designation.title
        else:
            return None

    def get_employeeskill(self, obj):
        skills = EmployeeSkill.objects.filter(employee=obj)
        return [
            {"skill": skill.skill.title, "percentage": skill.percentage}
            for skill in skills
        ]


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = [
            "created_at",
            "updated_at",
            "created_by",
        ]


class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class BlogTagSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField("get_id")
    slug = serializers.SerializerMethodField("get_slug")
    name = serializers.SerializerMethodField("get_name")

    class Meta:
        model = BlogTag
        fields = ("id", "slug", "name")

    def get_id(self, instance):
        return instance.tag.id

    def get_slug(self, instance):
        return instance.tag.slug

    def get_name(self, instance):
        return instance.tag.name

    # def to_representation(self, instance):
    #     return {
    #         'id': instance.id,
    #         'slug': instance.tag.slug,
    #         'name': instance.tag.name,
    #     }


class BlogCategoriesSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField("get_id")
    slug = serializers.SerializerMethodField("get_slug")
    name = serializers.SerializerMethodField("get_name")

    class Meta:
        model = BlogCategory
        fields = ("id", "slug", "name")

    def get_id(self, instance):
        return instance.category.id

    def get_slug(self, instance):
        return instance.category.slug

    def get_name(self, instance):
        return instance.category.name

    # def to_representation(self, instance):
    #     return {
    #         'id': instance.id,
    #         'slug': instance.category.slug,
    #         'name': instance.category.name,
    #     }


class AuthorSerializer(serializers.ModelSerializer):
    designation = serializers.CharField(source="designation.title", read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "full_name", "image", "designation")


class BlogContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogContext
        fields = ["id", "title", "description", "image", "video"]


class BlogSitemapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ("slug", "updated_at")


class BlogListSerializer(serializers.ModelSerializer):
    # categories = BlogCategoriesSerializer(many=True, source='blogcategory_set')
    category = serializers.SerializerMethodField("get_category")
    author = AuthorSerializer(source="created_by.employee")
    blog_contexts = BlogContextSerializer(many=True)

    class Meta:
        model = Blog
        fields = (
            "id",
            "slug",
            "title",
            # "short_description",
            "image",
            "category",
            "read_time_minute",
            "total_view",
            "created_at",
            "author",
            "blog_contexts",
        )

    def get_category(self, instance):
        blogcategory = instance.blogcategory_set.first()
        if blogcategory:
            return blogcategory.category.name
        return "-"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["categories"] = CategoryListSerializer(
            instance=instance.category, many=True
        ).data
        data["table_of_contents"] = instance.blog_contexts.all().values("id", "title")
        return data


class BlogFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogFAQ
        fields = ["question", "answer"]


class BlogMetadataSerializer(serializers.ModelSerializer):
    keywords = serializers.SerializerMethodField()

    class Meta:
        model = BlogMeatadata
        fields = ("title", "description", "canonical", "keywords")

    def get_keywords(self, obj):
        return [keyword.name for keyword in obj.blogkeyword_set.all()]


class BlogSEOEssentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogSEOEssential
        fields = ("title", "description", "keywords")


class BlogDetailsSerializer(BlogListSerializer):
    tags = TagSerializer(many=True, source="tag")
    blog_contexts = BlogContextSerializer(many=True)
    blog_faqs = BlogFAQSerializer(many=True)
    metadata = BlogMetadataSerializer(many=True, source="blogmeatadata_set")

    class Meta(BlogListSerializer.Meta):
        fields = (
            "id",
            "slug",
            "title",
            "total_view",
            # "short_description",
            "image",
            "category",
            "tags",
            "read_time_minute",
            "created_at",
            "author",
            "content",
            "blog_contexts",
            "blog_faqs",
            "metadata",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["total_blogs"] = instance.created_by.website_blog_related.filter(
            status=BlogStatus.APPROVED
        ).count()
        data["total_comments"] = instance.comments.count()
        data["table_of_contents"] = instance.blog_contexts.all().values("id", "title")
        data["seo_essential"] = BlogSEOEssentialSerializer(
            BlogSEOEssential.objects.filter(blog=instance), many=True
        ).data
        return data


class EmployeeDetailforNOCSerializer(serializers.ModelSerializer):
    designation = serializers.StringRelatedField()
    resignation_date = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            "slug",
            "full_name",
            "joining_date",
            "permanent_date",
            "resignation_date",
            "designation",
            "image",
        )

    def get_resignation_date(self, instance):
        res = instance.resignation_set.last()
        return res.date if res else None


class EmployeeNOCSerializer(serializers.ModelSerializer):
    document_type = serializers.SerializerMethodField()
    document_url = serializers.FileField(source="noc_pdf")
    document_preview = serializers.ImageField(source="noc_image")

    employee = EmployeeDetailforNOCSerializer(read_only=True)

    class Meta:
        model = EmployeeNOC
        fields = (
            "uuid",
            "document_type",
            "document_url",
            "document_preview",
            "employee",
        )

    def get_document_type(self, *args, **kwargs):
        return "NOC"


class BlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = [
            "id",
            "name",
            "email",
            "content",
            "blog",
            "parent",
            "created_at",
            "updated_at",
        ]


class OurTechnologySerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True)

    class Meta:
        model = OurTechnology
        fields = ("title", "technologies")


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("question", "answer")
        ref_name = "website_faq"


class OurClientsFeedbackSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="name", read_only=True)
    client_designation = serializers.CharField(source="designation", read_only=True)
    client_logo = serializers.ImageField(source="logo", read_only=True)
    feedback = serializers.SerializerMethodField()
    country = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = Client
        fields = (
            "client_name",
            "client_designation",
            "client_logo",
            "company_name",
            "feedback",
            "country",
            "client_feedback",
            "image",
        )

    # def get_client_name(self, obj):
    #     return obj.client.name if obj.client else None

    # def get_client_designation(self, obj):
    #     return obj.client.designation if obj.client else None

    # def get_client_logo(self, obj):
    #     if obj.client and obj.client.logo:
    #         return self.context["request"].build_absolute_uri(obj.client.logo.url)
    #     return None

    def get_feedback(self, obj):
        clientfeedback = ClientFeedback.objects.filter(project__client=obj)
        serializers = ClientFeedbackSerializer(instance=clientfeedback, many=True)
        return serializers.data


class OurAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurAchievement
        fields = ("title", "number", "icon")


class OurGrowthSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurGrowth
        fields = ("title", "number")


class OurJourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = OurJourney
        fields = ("year", "title", "description", "img")


class EmployeePerspectiveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    employee_designation = serializers.CharField(
        source="employee.designation", read_only=True
    )
    employee_image = serializers.ImageField(source="employee.image", read_only=True)

    class Meta:
        model = EmployeePerspective
        fields = (
            "title",
            "description",
            "employee_name",
            "employee_designation",
            "employee_image",
        )


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ["name", "email", "message", "file"]


class ClientLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["logo"]


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ["image"]


class LifeAtMediuswareSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifeAtMediusware
        fields = ["image"]


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = [
            "title",
            "image",
            "link",
            "short_description",
        ]


class ClientSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ["name", "designation", "image", "client_feedback"]

    def get_name(self, obj):
        return obj.web_name if obj.web_name else obj.name


class VideoTestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTestimonial
        fields = ["name", "client_image", "designation", "text", "video", "description"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["country"] = instance.country.name
        return data


class IndustryWeServeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryWeServe
        fields = ["title", "image", "slug"]


class OfficeLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeLocation
        fields = ["office", "address", "contact", "image", "email"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "brandphoto"]


# Define serializers for related models with only 'title' and 'sub_title'
class ModelTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelTitle
        fields = ["title", "sub_title"]


class AwardsTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwardsTitle
        fields = ["title", "sub_title"]


class WhyUsTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhyUsTitle
        fields = ["title", "sub_title"]


class AllServicesTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllServicesTitle
        fields = ["title", "sub_title"]


class TechnologyTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyTitle
        fields = ["title", "sub_title"]


class VideoTestimonialTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTestimonialTitle
        fields = ["title", "sub_title"]


class IndustryTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryTitle
        fields = ["title", "sub_title"]


class LifeAtMediuswareTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifeAtMediuswareTitle
        fields = ["title", "sub_title"]


class ProjectsVideoTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectsVideoTitle
        fields = ["title", "sub_title"]


class BlogTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTitle
        fields = ["title", "sub_title"]


class TextualTestimonialTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextualTestimonialTitle
        fields = ["title", "sub_title"]


class SpecialProjectsTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialProjectsTitle
        fields = ["title", "sub_title"]


class FAQHomeTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQHomeTitle
        fields = ["title", "sub_title"]


class OurJourneyTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurJourneyTitle
        fields = ["title", "sub_title"]


class BaseTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectServiceSolutionTitle
        fields = ["title", "sub_title"]


# Define the WebsiteTitleSerializer with related fields
class WebsiteTitleSerializer(serializers.ModelSerializer):
    model_title = ModelTitleSerializer(source="modeltitle", read_only=True)
    awards_title = AwardsTitleSerializer(source="awardstitle", read_only=True)
    why_us_title = WhyUsTitleSerializer(source="whyustitle", read_only=True)
    all_services_title = AllServicesTitleSerializer(
        source="allservicestitle", read_only=True
    )
    technology_title = TechnologyTitleSerializer(
        source="technologytitle", read_only=True
    )
    video_testimonial_title = VideoTestimonialTitleSerializer(
        source="videotestimonialtitle", read_only=True
    )
    industry_title = IndustryTitleSerializer(source="industrytitle", read_only=True)
    life_at_mediusware_title = LifeAtMediuswareTitleSerializer(
        source="lifeatmediuswaretitle", read_only=True
    )
    projects_video_title = ProjectsVideoTitleSerializer(
        source="projectsvideotitle", read_only=True
    )
    blog_title = BlogTitleSerializer(source="blogtitle", read_only=True)
    textual_testimonial_title = TextualTestimonialTitleSerializer(
        source="textualtestimonialtitle", read_only=True
    )
    special_projects_title = SpecialProjectsTitleSerializer(
        source="specialprojectstitle", read_only=True
    )
    faq_home_title = FAQHomeTitleSerializer(source="faqhometitle", read_only=True)
    our_journey_title = OurJourneyTitleSerializer(
        source="ourjourneytitle", read_only=True
    )
    project_service_solution = BaseTitleSerializer(
        source="projectservicesolutiontitle", read_only=True
    )
    project_key_feature = BaseTitleSerializer(
        source="projectkeyfeaturetitle", read_only=True
    )
    project_results = BaseTitleSerializer(source="projectresultstitle", read_only=True)
    project_screenshot = BaseTitleSerializer(
        source="projectscreenshottitle", read_only=True
    )
    project_technology = BaseTitleSerializer(
        source="projecttechnologytitle", read_only=True
    )
    project_client_review = BaseTitleSerializer(
        source="projectclientreviewtitle", read_only=True
    )
    employee_testimonial = BaseTitleSerializer(
        source="employeetestimonialtitle", read_only=True
    )
    benefits = BaseTitleSerializer(source="benefitsofemploymenttitle", read_only=True)

    class Meta:
        model = WebsiteTitle
        fields = "__all__"


class BaseBannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        exclude = ["page_banner", "created_at", "updated_at"]


class PageBannerSerializer(serializers.ModelSerializer):
    home = BaseBannerImageSerializer(source="homebanner", read_only=True)
    why_we_are = BaseBannerImageSerializer(source="whywearebanner", read_only=True)
    woman_empowerment = BaseBannerImageSerializer(
        source="womenempowermentbanner", read_only=True
    )
    csr = BaseBannerImageSerializer(source="csrbanner", read_only=True)
    delivery_model = BaseBannerImageSerializer(
        source="deliverymodelbanner", read_only=True
    )
    engagement_model = BaseBannerImageSerializer(
        source="engagementmodelbanner", read_only=True
    )
    development_methodology = BaseBannerImageSerializer(
        source="developmentmethodologybanner", read_only=True
    )
    client_testimonial = BaseBannerImageSerializer(
        source="clienttestimonialbanner", read_only=True
    )
    clutch_testimonial = BaseBannerImageSerializer(
        source="clutchtestimonialbanner", read_only=True
    )
    award = BaseBannerImageSerializer(source="awardsbanner", read_only=True)
    contact = BaseBannerImageSerializer(source="contactbanner", read_only=True)
    all_projects = BaseBannerImageSerializer(source="allprojectsbanner", read_only=True)
    leader_ship = BaseBannerImageSerializer(source="leadershipbanner", read_only=True)
    career = BaseBannerImageSerializer(source="careerbanner", read_only=True)

    class Meta:
        model = PageBanner
        exclude = ["id", "created_at", "updated_at"]


class ProjectTechnologyCountSerializer(serializers.ModelSerializer):
    project_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Technology
        fields = ["name", "project_count"]

    # def get_project_count(self, obj):
    #     from django.db.models import Count

    #     p = Technology.objects.annotate(
    #         project_count=Count("projecttechnology__project")
    #     ).values("name", "project_count")
    #     return Project.objects.filter(
    #         show_in_website=True, projecttechnology__technologies=obj
    #     ).count()


class ClientReviewSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    project_title = serializers.CharField(source="web_title")

    class Meta:
        model = Project
        fields = [
            "project_title",
            "project_logo",
            "client_web_name",
            "client_image",
            "client_review",
            "country",
        ]

    def get_country(self, obj):
        if obj.country is None:
            return None
        return obj.country.name


class LeaderSerializer(serializers.ModelSerializer):
    designation = serializers.CharField(source="designation.title")

    class Meta:
        model = Employee
        fields = ("full_name", "designation")


class LeadershipSpeechSerializer(serializers.ModelSerializer):
    leader = LeaderSerializer(read_only=True)

    class Meta:
        model = LeadershipSpeech
        exclude = ["leadership", "created_at", "updated_at"]


class LeadershipSerializer(serializers.ModelSerializer):
    speeches = LeadershipSpeechSerializer(many=True)

    class Meta:
        model = Leadership
        exclude = ["created_at", "updated_at"]


class EmployeeTestimonialSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name")

    class Meta:
        model = EmployeeTestimonial
        exclude = ["created_at", "updated_at", "employee", "career"]


class BenefitsOfEmploymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenefitsOfEmployment
        exclude = ["created_at", "updated_at", "career"]


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = "__all__"



class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"