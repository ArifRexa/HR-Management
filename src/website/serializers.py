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
    CTA,
    FAQ,
    AdditionalPageFAQ,
    AdditionalPageHeroSection,
    AdditionalPageKeyThings,
    AdditionalPageKeyThingsCards,
    AdditionalPageOurProcess,
    AdditionalPageWhyChooseUs,
    AdditionalPages,
    AllServicesTitle,
    Award,
    AwardCategory,
    AwardYearGroup,
    Awards,
    AwardsHomePage,
    AwardsTitle,
    BeginningOfWorking,
    BenefitsOfEmployment,
    Blog,
    BlogCategory,
    BlogComment,
    BlogContext,
    BlogFAQ,
    BlogFAQSchema,
    BlogMeatadata,
    BlogModeratorFeedback,
    BlogSEOEssential,
    BlogStatus,
    BlogTag,
    BlogTitle,
    BlogsAndArticlesHomePage,
    Brand,
    CaseStudyHomePage,
    Category,
    Certification,
    Contact,
    ContactForm,
    EcoSystem,
    EcoSystemCardTags,
    EcoSystemCards,
    EmployeePerspective,
    EmployeeTestimonial,
    FAQHomeTitle,
    Gallery,
    HistoryOfTech,
    HomeBanner,
    HomePage,
    HomePageHeroAnimatedTitle,
    Industry,
    IndustryTitle,
    IndustryWeServe,
    IndustryWeServeHomePage,
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
    OurProcessHome,
    PageBanner,
    PostCredential,
    ProjectMetadata,
    ProjectServiceSolutionTitle,
    ProjectsVideoTitle,
    ReferenceBlogs,
    RelatedBlogs,
    Service,
    ServiceContent,
    ServiceMeatadata,
    ServiceProcess,
    ServicesWeProvide,
    ServicesWeProvideCards,
    SpecialProjectsTitle,
    Subscription,
    TeamElement,
    TechStack,
    TechnologyCTA,
    TechnologyCreatorsQuotes,
    TechnologyFAQ,
    TechnologyFAQSchema,
    TechnologyKeyThings,
    TechnologyKeyThingsQA,
    TechnologyOurProcess,
    TechnologySolutionsAndServices,
    TechnologySolutionsAndServicesCards,
    TechnologyTitle,
    TechnologyType,
    TechnologyWhyChooseUs,
    TechnologyWhyChooseUsCards,
    TechnologyWhyChooseUsCardsDetails,
    TestimonialsHomePage,
    TextualTestimonialTitle,
    VideoTestimonial,
    VideoTestimonialTitle,
    WebsiteTitle,
    WhatIs,
    WhyUsTitle,
)
from website.models_v2.industries_we_serve import ApplicationAreas, Benefits, BenefitsQA, CustomSolutions, CustomSolutionsCards, IndustryDetailsHeading, IndustryDetailsHeadingCards, IndustryDetailsHeroSection, IndustryItemTags, IndustryServe, OurProcess, ServeCategory, ServeCategoryCTA, ServeCategoryFAQSchema, ServiceCategoryFAQ, WhyChooseUs, WhyChooseUsCards, WhyChooseUsCardsDetails
from website.models_v2.services import AdditionalServiceContent, BestPracticesCards, BestPracticesCardsDetails, BestPracticesHeadings, ComparativeAnalysis, DevelopmentServiceProcess, DiscoverOurService, KeyThings, KeyThingsQA, MetaDescription, ServiceCriteria, ServiceFAQQuestion, ServiceMetaData, ServicePage, ServicePageCTA, ServicePageFAQSchema, ServicesItemTags, ServicesOurProcess, ServicesWhyChooseUs, ServicesWhyChooseUsCards, ServicesWhyChooseUsCardsDetails, SolutionsAndServices, SolutionsAndServicesCards



class HomePageAnimateTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePageHeroAnimatedTitle
        fields = ("title",)


class BeginningOfWorkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeginningOfWorking
        fields = ("seo_title", "section_title", "secondary_title", "section_description")


class IndustryWeServeHomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryWeServeHomePage
        fields = ("seo_title", "section_title", "secondary_title", "section_description")


class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ("seo_title", "section_title", "secondary_title", "section_description")


class TestimonialsHomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestimonialsHomePage
        fields = ("seo_title", "section_title", "secondary_title", "section_description")


class AwardsHomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwardsHomePage
        fields = ("seo_title", "section_title", "secondary_title", "section_description")


class BlogsAndArticlesHomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogsAndArticlesHomePage
        fields = ("seo_title", "section_title", "secondary_title", "section_description")


class CaseStudyHomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseStudyHomePage
        fields = ("seo_title", "section_title", "secondary_title", "section_description")


class OurProcessHomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurProcessHome
        fields = ("id", "section_title", "section_description", "order")


class HomePageSerializer(serializers.ModelSerializer):
    animated_titles = HomePageAnimateTitleSerializer(
        many=True,
        source='hero_animated_titles',
        read_only=True
    )
    beginning_of_working = BeginningOfWorkingSerializer(many=True, read_only=True)
    industry_we_serve = IndustryWeServeHomePageSerializer(many=True, read_only=True)
    tech_stack = TechStackSerializer(many=True, read_only=True)
    testimonials = TestimonialsHomePageSerializer(many=True, read_only=True)
    awards = AwardsHomePageSerializer(many=True, read_only=True)
    blogs_and_articles = BlogsAndArticlesHomePageSerializer(many=True, read_only=True)
    case_studies = CaseStudyHomePageSerializer(many=True, read_only=True)
    our_process_home = OurProcessHomeSerializer(many=True, read_only=True)

    class Meta:
        model = HomePage
        fields = (
            "id",
            "seo_title",
            "section_title",
            "section_description",
            "button_text",
            "button_url",
            # Nested Sections
            "animated_titles",
            "beginning_of_working",
            "industry_we_serve",
            "tech_stack",
            "testimonials",
            "awards",
            "blogs_and_articles",
            "case_studies",
            "our_process_home",
        )

# class HomePageSerializer(serializers.ModelSerializer):
#     animated_titles = HomePageAnimateTitleSerializer(
#         many=True, 
#         source='hero_animated_titles',
#         read_only=True
#     )
    
#     class Meta:
#         model = HomePage
#         fields = (
#             "id",
#             "seo_title",
#             "section_title",
#             "section_description",
#             "button_text",
#             "button_url",
#             "animated_titles",
#         )









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
        fields = ("title",)


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
    

class CardTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionsAndServicesCards
        fields = ['card_title']

class ServicePageCardTitlesSerializer(serializers.ModelSerializer):
    card_titles = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicePage
        fields = ['card_titles']
    
    def get_card_titles(self, obj):
        # Get all related SolutionsAndServices
        solutions_services = obj.solutions_and_services.all()
        
        # Get all cards from all solutions services
        cards = SolutionsAndServicesCards.objects.filter(
            solutions_and_services__in=solutions_services
        )
        
        # Extract all card titles
        return [card.card_title for card in cards]


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


class TechnologyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyType
        fields = ['name', 'slug']

class NewTechnologySerializer(serializers.ModelSerializer):
    type = TechnologyTypeSerializer(read_only=True)
    
    class Meta:
        from website.models import Technology
        model = Technology
        fields = ['name', 'slug', 'type'] 

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
    industries = ProjectIndustrySerializer(many=True)  # Added many=True
    services = ProjectServiceSerializer(many=True)
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
        fields = ("title", "content", "image", "image2", "video_url", "iframe")


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

class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = "__all__"

    def validate(self, data):
        form_type = data.get('form_type')
        full_name = data.get('full_name')
        email = data.get('email')
        service_require = data.get('service_require')
        client_query = data.get('client_query')

        # Common required fields
        if not full_name:
            raise serializers.ValidationError({"full_name": "This field is required."})
        if not email:
            raise serializers.ValidationError({"email": "This field is required."})

        # Conditional required fields based on form_type
        if form_type == 'discuss':
            if not service_require:
                raise serializers.ValidationError({"service_require": "This field is required for Discuss Service form type."})
        elif form_type == 'general':
            if not client_query:
                raise serializers.ValidationError({"client_query": "This field is required for General Inquiry form type."})

        return data

class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = "__all__"



class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"



# ==================================== Blog API Serializers ================================
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        from website.models import Tag
        model = Tag
        fields = ['id', 'name', 'slug']
        ref_name = 'website_tag'


class ServicePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePage
        fields = ['id', 'title', 'slug', 'is_parent', 'h1_title', 'sub_title', 'description']
        ref_name = 'website_servicepage'

class ServeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServeCategory
        fields = ['id', 'title', 'slug']
        ref_name = 'website_servecategory'

class SimpleServeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServeCategory
        fields = ['id', 'title', 'slug']



class TechnologyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyType
        fields = ['id', 'name', 'slug']

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        from website.models import Technology
        model = Technology
        fields = ['id', 'name', 'slug', 'icon']  # Include icon if needed
        ref_name = 'website_technology'

class BlogContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogContext
        fields = '__all__'
        ref_name = 'website_blogcontext'

class BlogFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogFAQ
        fields = '__all__'
        ref_name = 'website_blogfaq'

class BlogSEOEssentialSerializers(serializers.ModelSerializer):
    class Meta:
        model = BlogSEOEssential
        fields = ['id', 'title', 'description', 'keywords', 'created_at', 'updated_at']
        ref_name = 'website_blogseoessential'

class ReferenceBlogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceBlogs
        fields = ['id', 'reference_blog_title', 'reference_blog_link']
        ref_name = 'website_referenceblog'

class RelatedBlogsSerializer(serializers.ModelSerializer):
    releted_blog = serializers.StringRelatedField()  # To avoid recursion, use string or id

    class Meta:
        model = RelatedBlogs
        fields = ['id', 'releted_blog']
        ref_name = 'website_relatedblogs'

class BlogFAQSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogFAQSchema
        fields = '__all__'

class BlogModeratorFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogModeratorFeedback
        fields = '__all__'

# class CTASerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CTA
#         fields = '__all__'

class BlogSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    tag = TagSerializer(many=True, read_only=True)
    parent_services = ServicePageSerializer(many=True, read_only=True)
    child_services = ServicePageSerializer(many=True, read_only=True)
    industry_details = ServeCategorySerializer(many=True, read_only=True)
    technology_type = TechnologyTypeSerializer(read_only=True)
    technology = TechnologySerializer(many=True, read_only=True)
    blog_contexts = BlogContextSerializer(many=True, read_only=True)
    blog_faqs = BlogFAQSerializer(many=True, read_only=True)
    seo_essential = BlogSEOEssentialSerializers(source='blogseoessential_set', many=True, read_only=True)
    reference_blogs = ReferenceBlogsSerializer(source='reference_blog', many=True, read_only=True)
    related_blogs = RelatedBlogsSerializer(source='relatedblogs_set', many=True, read_only=True)
    faq_schema = BlogFAQSchemaSerializer(read_only=True)
    moderator_feedbacks = BlogModeratorFeedbackSerializer(source='blogmoderatorfeedback_set', many=True, read_only=True)
    # ctas = CTASerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField()
    table_of_contents = serializers.SerializerMethodField()


    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'image', 'youtube_link', 'category', 'industry_details',
            'parent_services', 'child_services', 'technology_type', 'technology', 'tag',
            'is_featured', 'schema_type', 'main_body_schema', 'hightlighted_text', 'cta_title', 'status',
            'total_view', 'created_at', 'updated_at', 'approved_at', 'read_time_minute',
            'author', 'blog_contexts', 'blog_faqs', 'seo_essential',
            'reference_blogs', 'related_blogs', 'faq_schema', 'moderator_feedbacks', 'table_of_contents'
        ]
        ref_name = 'website_blog'

    def get_author(self, obj):
        author = obj.author
        return f"{author}" if author else ""
    
    def get_table_of_contents(self, obj):
        """
        Returns a list of all titles from this blog's contexts
        """
        # Get all contexts for this blog ordered by their sequence or creation date
        contexts = obj.blog_contexts.all()
        
        # Extract just titles titles from each context
        return [context.title for context in contexts]
    




# ============================== Industry Details ==================================


class IndustryDetailsHeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryDetailsHeroSection
        fields = '__all__'
        ref_name = 'IndustriesWeServeIndustryDetailsHeroSection'

class IndustryDetailsHeadingCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryDetailsHeadingCards
        fields = '__all__'
        ref_name = 'IndustriesWeServeIndustryDetailsHeadingCards'

class CustomSolutionsCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomSolutionsCards
        fields = '__all__'
        ref_name = 'IndustriesWeServeCustomSolutionsCards'

class BenefitsQASerializer(serializers.ModelSerializer):
    class Meta:
        model = BenefitsQA
        fields = '__all__'
        ref_name = 'IndustriesWeServeBenefitsQA'


class WhyChooseUsCardsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhyChooseUsCardsDetails
        fields = '__all__'
        ref_name = 'IndustriesWeServeWhyChooseUsCardsDetails'


class WhyChooseUsCardsSerializer(serializers.ModelSerializer):
    details = WhyChooseUsCardsDetailsSerializer(many=True, read_only=True, source='why_choose_us_cards_details.all')
    class Meta:
        model = WhyChooseUsCards
        fields = '__all__'
        ref_name = 'IndustriesWeServeWhyChooseUsCards'

class OurProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurProcess
        fields = '__all__'
        ref_name = 'IndustriesWeServeOurProcess'

class IndustryDetailsHeadingSerializer(serializers.ModelSerializer):
    industry_details_sub_heading = IndustryDetailsHeadingCardsSerializer(many=True, read_only=True)
    
    class Meta:
        model = IndustryDetailsHeading
        fields = '__all__'
        ref_name = 'IndustriesWeServeIndustryDetailsHeading'

class CustomSolutionsSerializer(serializers.ModelSerializer):
    custom_solutions_cards = CustomSolutionsCardsSerializer(many=True, read_only=True)
    
    class Meta:
        model = CustomSolutions
        fields = '__all__'
        ref_name = 'IndustriesWeServeCustomSolutions'

class BenefitsSerializer(serializers.ModelSerializer):
    benefits_cards = BenefitsQASerializer(many=True, read_only=True)
    
    class Meta:
        model = Benefits
        fields = '__all__'
        ref_name = 'IndustriesWeServeBenefits'

class WhyChooseUsSerializer(serializers.ModelSerializer):
    cards = WhyChooseUsCardsSerializer(many=True, read_only=True, source='why_choose_us_cards.all')
    
    class Meta:
        model = WhyChooseUs
        fields = '__all__'
        ref_name = 'IndustriesWeServeWhyChooseUs'

class ServeCategoryCTASerializer(serializers.ModelSerializer):
    class Meta:
        model = ServeCategoryCTA
        fields = '__all__'
        ref_name = 'IndustriesWeServeServeCategoryCTA'

class ServiceCategoryFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategoryFAQ
        fields = '__all__'
        ref_name = 'IndustriesWeServeServiceCategoryFAQ'

class ServeCategoryFAQSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServeCategoryFAQSchema
        fields = '__all__'
        ref_name = 'IndustriesWeServeServeCategoryFAQSchema'

class ApplicationAreasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationAreas
        fields = '__all__'
        ref_name = 'IndustriesWeServeApplicationAreas'

class IndustryServeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryServe
        fields = '__all__'
        ref_name = 'IndustriesWeServeIndustryServe'



class ServeCategorySerializer(serializers.ModelSerializer):
    # Change these fields to return single objects instead of arrays
    industry_details_hero_section = serializers.SerializerMethodField()
    industry_solutions_and_services = serializers.SerializerMethodField()
    industry_benifits = serializers.SerializerMethodField()
    benifited_organizations = serializers.SerializerMethodField()
    why_choose_us = WhyChooseUsSerializer(many=True, read_only=True)
    our_process = OurProcessSerializer(many=True, read_only=True)
    faqs = ServiceCategoryFAQSerializer(many=True, read_only=True)
    ctas = ServeCategoryCTASerializer(many=True, read_only=True)
    faq_schema = ServeCategoryFAQSchemaSerializer(read_only=True)
    # application_areas = ApplicationAreasSerializer(many=True, read_only=True)
    industries = IndustryServeSerializer(many=True, read_only=True)
    table_of_contents = serializers.SerializerMethodField()
    
    class Meta:
        model = ServeCategory
        fields = '__all__'
        ref_name = 'IndustriesWeServeServeCategory'

    def get_industry_details_hero_section(self, obj):
        try:
            item = obj.industry_details_hero_section.first()
            if item:
                return IndustryDetailsHeroSectionSerializer(item, context=self.context).data
            return None
        except AttributeError:
            return None
    
    def get_industry_solutions_and_services(self, obj):
        try:
            item = obj.industry_details_heading.first()
            if item:
                return IndustryDetailsHeadingSerializer(item, context=self.context).data
            return None
        except AttributeError:
            return None
    
    def get_industry_benifits(self, obj):
        try:
            item = obj.custom_solutions.first()
            if item:
                return CustomSolutionsSerializer(item, context=self.context).data
            return None
        except AttributeError:
            return None
    
    def get_benifited_organizations(self, obj):
        try:
            item = obj.benefits.first()
            if item:
                return BenefitsSerializer(item, context=self.context).data
            return None
        except AttributeError:
            return None
    
    def get_table_of_contents(self, obj):
        toc = []
        
        # Add section titles from Industry Details Hero Section
        try:
            for item in obj.industry_details_hero_section.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add section titles from Our Process
        # try:
        #     for item in obj.our_process.all():
        #         if item.section_title:
        #             toc.append(item.section_title)
        # except AttributeError:
        #     pass
        
        # Add section titles from Industry Solutions and Services (using model field name)
        try:
            for item in obj.industry_details_heading.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add section titles from Industry Benefits (using model field name)
        try:
            for item in obj.custom_solutions.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add section titles from Benefited Organizations (using model field name)
        try:
            for item in obj.benefits.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add section titles from Why Choose Us
        try:
            for item in obj.why_choose_us.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add titles from Application Areas
        try:
            for item in obj.application_areas.all():
                if item.title:
                    toc.append(item.title)
        except AttributeError:
            pass
        
        # Add titles from Industries
        try:
            for item in obj.industries.all():
                if item.title:
                    toc.append(item.title)
        except AttributeError:
            pass
        
        return toc


class IndustryItemTagSerializer(serializers.ModelSerializer):
    """Serializer for IndustryItemTags model (title field only)"""
    class Meta:
        model = IndustryItemTags
        fields = ['title']

class IndustryDetailsHeroSerializer(serializers.ModelSerializer):
    """Serializer for IndustryDetailsHeroSection model (section_description field only)"""
    class Meta:
        model = IndustryDetailsHeroSection
        fields = ['section_description']

class ServeCategoryMainSerializer(serializers.ModelSerializer):
    """Main serializer combining all required fields"""
    # Get section_description from related hero section
    section_description = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = ServeCategory
        fields = [
            'title',
            'slug',
            'show_in_menu',
            'section_description',
            'tags'
        ]

    def get_section_description(self, obj):
        """Get the section description from the most recent hero section"""
        hero_section = obj.industry_details_hero_section.order_by('-created_at').first()
        return hero_section.section_description if hero_section else None

    def get_tags(self, obj):
        """Get all related tag titles"""
        return [tag.title for tag in obj.industry_item_tags.all()]

# ===================================================== ServicesPage =====================================================

class ServicesItemTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicesItemTags
        fields = '__all__'
        ref_name = 'ServiceItemTag'
# Base serializers for nested models
class SolutionsAndServicesCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionsAndServicesCards
        fields = '__all__'
        ref_name = 'SolutionServiceCard'

class SolutionsAndServicesSerializer(serializers.ModelSerializer):
    cards = SolutionsAndServicesCardsSerializer(many=True, read_only=True)
    
    class Meta:
        model = SolutionsAndServices
        fields = '__all__'
        ref_name = 'SolutionService'

class KeyThingsQASerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyThingsQA
        fields = '__all__'
        ref_name = 'KeyThingQA'

class KeyThingsSerializer(serializers.ModelSerializer):
    KeyThings_cards = KeyThingsQASerializer(many=True, read_only=True)
    
    class Meta:
        model = KeyThings
        fields = '__all__'
        ref_name = 'KeyThing'

class BestPracticesCardsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestPracticesCardsDetails
        fields = '__all__'
        ref_name = 'BestPracticeCardDetail'

class BestPracticesCardsSerializer(serializers.ModelSerializer):
    details = BestPracticesCardsDetailsSerializer(many=True, read_only=True)
    
    class Meta:
        model = BestPracticesCards
        fields = '__all__'
        ref_name = 'BestPracticeCard'

class BestPracticesHeadingsSerializer(serializers.ModelSerializer):
    cards = BestPracticesCardsSerializer(many=True, read_only=True)
    
    class Meta:
        model = BestPracticesHeadings
        fields = '__all__'
        ref_name = 'BestPracticeHeading'

class ServicesWhyChooseUsCardsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicesWhyChooseUsCardsDetails
        fields = '__all__'
        ref_name = 'WhyChooseUsCardDetail'

class ServicesWhyChooseUsCardsSerializer(serializers.ModelSerializer):
    details = ServicesWhyChooseUsCardsDetailsSerializer(many=True, read_only=True)
    
    class Meta:
        model = ServicesWhyChooseUsCards
        fields = '__all__'
        ref_name = 'WhyChooseUsCard'

class ServicesWhyChooseUsSerializer(serializers.ModelSerializer):
    cards = ServicesWhyChooseUsCardsSerializer(many=True, read_only=True)
    
    class Meta:
        model = ServicesWhyChooseUs
        fields = '__all__'
        ref_name = 'WhyChooseUs'

class ServicesOurProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicesOurProcess
        fields = '__all__'
        ref_name = 'ServiceProcess'

class ServicePageFAQSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePageFAQSchema
        fields = '__all__'
        ref_name = 'ServiceFAQSchema'

class ServicePageCTASerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePageCTA
        fields = '__all__'
        ref_name = 'ServiceCTA'

class ServiceFAQQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFAQQuestion
        fields = '__all__'
        ref_name = 'ServiceFAQ'

class DiscoverOurServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscoverOurService
        fields = '__all__'
        ref_name = 'DiscoverService'

class AdditionalServiceContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalServiceContent
        fields = '__all__'
        ref_name = 'AdditionalServiceContents'

class DevelopmentServiceProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevelopmentServiceProcess
        fields = '__all__'
        ref_name = 'DevelopmentProcess'

class ServiceCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCriteria
        fields = '__all__'
        ref_name = 'ServiceCriteria'

class ComparativeAnalysisSerializer(serializers.ModelSerializer):
    criteria = ServiceCriteriaSerializer(read_only=True)
    
    class Meta:
        model = ComparativeAnalysis
        fields = '__all__'
        ref_name = 'ComparativeAnalys'

class ServiceMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMetaData
        fields = '__all__'
        ref_name = 'ServiceMetaData'


class ServicePageChildrenSerializer(serializers.ModelSerializer):
    tags = ServicesItemTagsSerializer(many=True, read_only=True, source='service_item_tags')
    class Meta:
        model = ServicePage
        fields = ['id', 'title', 'secondary_title', 'h1_title', 'slug', 'sub_title', 'description', 'show_in_menu', 'tags']
        ref_name = 'ServicePageChild'


class MetaDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaDescription
        fields = '__all__'
        ref_name = 'MetaDescription'
        
# Main ServicePage serializer with all nested relationships
class ServicePageDetailSerializer(serializers.ModelSerializer):
    children = ServicePageChildrenSerializer(many=True, read_only=True, source='children.all')
    solutions_and_services = SolutionsAndServicesSerializer(many=True, read_only=True)
    KeyThings = KeyThingsSerializer(many=True, read_only=True)
    best_practices = BestPracticesHeadingsSerializer(many=True, read_only=True)
    why_choose_us = ServicesWhyChooseUsSerializer(many=True, read_only=True)
    our_process = ServicesOurProcessSerializer(many=True, read_only=True)
    faq_schema = ServicePageFAQSchemaSerializer(read_only=True)
    ctas = ServicePageCTASerializer(many=True, read_only=True)
    questions = ServiceFAQQuestionSerializer(many=True, read_only=True)
    discover_services = DiscoverOurServiceSerializer(many=True, read_only=True)
    additional_service_content = AdditionalServiceContentSerializer(many=True, read_only=True)
    development_services_process = DevelopmentServiceProcessSerializer(many=True, read_only=True)
    comparative_analysis = ComparativeAnalysisSerializer(many=True, read_only=True)
    service_meta_data = ServiceMetaDataSerializer(read_only=True)
    table_of_contents = serializers.SerializerMethodField()
    meta_description = MetaDescriptionSerializer()
    
    class Meta:
        model = ServicePage
        fields = '__all__'
        depth = 1
        ref_name = 'ServicePageDetails'

    def get_table_of_contents(self, obj):
        toc = []
        
        # Add section titles from Solutions and Services
        try:
            for item in obj.solutions_and_services.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add section titles from Key Things
        try:
            for item in obj.KeyThings.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add section titles from Best Practices
        try:
            for item in obj.best_practices.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add section titles from Why Choose Us
        try:
            for item in obj.why_choose_us.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add section titles from Our Process
        try:
            for item in obj.our_process.all():
                if item.section_title:
                    toc.append(item.section_title)
        except AttributeError:
            pass
        
        # Add titles from Discover Our Service
        try:
            for item in obj.discover_services.all():
                if item.title:
                    toc.append(item.title)
        except AttributeError:
            pass
        
        # Add titles from Additional Service Content
        try:
            for item in obj.additional_service_content.all():
                if item.title:
                    toc.append(item.title)
        except AttributeError:
            pass
        
        # Add titles from Development Service Process
        try:
            for item in obj.development_services_process.all():
                if item.title:
                    toc.append(item.title)
        except AttributeError:
            pass

        try:
            for item in obj.meta_description.all():
                if item.title:
                    toc.append(item.title)
        except AttributeError:
            pass
        
        return toc


# ======================================== Technology API Serializers =========================================

class TechnologyCreatorsQuotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyCreatorsQuotes
        fields = '__all__'
        ref_name = 'TechnologyCreatorsQuotesSerializer'

class TechnologyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyType
        fields = '__all__'
        ref_name = 'TechnologyTypeSerializer'

class TechnologySolutionsAndServicesCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologySolutionsAndServicesCards
        fields = '__all__'
        ref_name = 'TechnologySolutionsAndServicesCardsSerializer'

class TechnologySolutionsAndServicesSerializer(serializers.ModelSerializer):
    cards = TechnologySolutionsAndServicesCardsSerializer(many=True, read_only=True)
    
    class Meta:
        model = TechnologySolutionsAndServices
        fields = '__all__'
        ref_name = 'TechnologySolutionsAndServicesSerializer'

class ServicesWeProvideCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicesWeProvideCards
        fields = '__all__'
        ref_name = 'ServicesWeProvideCardsSerializer'

class ServicesWeProvideSerializer(serializers.ModelSerializer):
    services_we_provide_cards = ServicesWeProvideCardsSerializer(many=True, read_only=True)
    
    class Meta:
        model = ServicesWeProvide
        fields = '__all__'
        ref_name = 'ServicesWeProvideSerializer'

class EcoSystemCardTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoSystemCardTags
        fields = '__all__'
        ref_name = 'EcoSystemCardTagsSerializer'

class EcoSystemCardsSerializer(serializers.ModelSerializer):
    ecosystem_card_tags = EcoSystemCardTagsSerializer(many=True, read_only=True)
    
    class Meta:
        model = EcoSystemCards
        fields = '__all__'
        ref_name = 'EcoSystemCardsSerializer'

class EcoSystemSerializer(serializers.ModelSerializer):
    ecosystem_cards = EcoSystemCardsSerializer(many=True, read_only=True)
    
    class Meta:
        model = EcoSystem
        fields = '__all__'
        ref_name = 'EcoSystemSerializer'

class TechnologyKeyThingsQASerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyKeyThingsQA
        fields = '__all__'
        ref_name = 'TechnologyKeyThingsQASerializer'

# class TechnologyKeyThingsSerializer(serializers.ModelSerializer):
#     tech_keythings_cards = TechnologyKeyThingsQASerializer(many=True, read_only=True)
    
#     class Meta:
#         model = TechnologyKeyThings
#         fields = '__all__'
#         ref_name = 'TechnologyKeyThingsSerializer'
class TechnologyKeyThingsSerializer(serializers.ModelSerializer):
    KeyThings_cards = TechnologyKeyThingsQASerializer(many=True, read_only=True, source='Tech_KeyThings_cards')  # Changed from tech_keythings_cards
    
    class Meta:
        model = TechnologyKeyThings
        fields = '__all__'
        ref_name = 'TechnologyKeyThingsSerializer'

class TechnologyWhyChooseUsCardsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyWhyChooseUsCardsDetails
        fields = '__all__'
        ref_name = 'TechnologyWhyChooseUsCardsDetailsSerializer'

class TechnologyWhyChooseUsCardsSerializer(serializers.ModelSerializer):
    details = TechnologyWhyChooseUsCardsDetailsSerializer(many=True, read_only=True, source = 'tech_why_choose_us_card_details')
    
    class Meta:
        model = TechnologyWhyChooseUsCards
        fields = '__all__'
        ref_name = 'TechnologyWhyChooseUsCardsSerializer'

# class TechnologyWhyChooseUsSerializer(serializers.ModelSerializer):
#     tech_why_choose_us_cards = TechnologyWhyChooseUsCardsSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = TechnologyWhyChooseUs
#         fields = '__all__'
#         ref_name = 'TechnologyWhyChooseUsSerializer'
class TechnologyWhyChooseUsSerializer(serializers.ModelSerializer):
    cards = TechnologyWhyChooseUsCardsSerializer(many=True, read_only=True, source='Tech_why_choose_us_cards')  # Changed from tech_why_choose_us_cards

    class Meta:
        model = TechnologyWhyChooseUs
        fields = '__all__'
        ref_name = 'TechnologyWhyChooseUsSerializer'

class TechnologyOurProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyOurProcess
        fields = '__all__'
        ref_name = 'TechnologyOurProcessSerializer'

class HistoryOfTechSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryOfTech
        fields = '__all__'
        ref_name = 'HistoryOfTechSerializer'

class TechnologyFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyFAQ
        fields = '__all__'
        ref_name = 'TechnologyFAQSerializer'

class TechnologyCTASerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyCTA
        fields = '__all__'
        ref_name = 'TechnologyCTASerializer'

class TechnologyFAQSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnologyFAQSchema
        fields = '__all__'
        ref_name = 'TechnologyFAQSchemaSerializer'

class TechnologyListSerializer(serializers.ModelSerializer):
    type = TechnologyTypeSerializer(read_only=True)
    
    class Meta:
        from website.models import Technology
        model = Technology
        fields = ['id', 'name', 'slug', 'type', 'icon', 'show_in_menu']
        ref_name = 'TechnologyListSerializer'


class TechnologySiteMapSerializer(serializers.ModelSerializer):
    
    class Meta:
        from website.models import Technology
        model = Technology
        fields = ['slug', 'updated_at']
        ref_name = 'TechnologySiteMapSerializer'

# class TechnologyDetailSerializer(serializers.ModelSerializer):
#     type = TechnologyTypeSerializer(read_only=True)
#     solutions_and_services = TechnologySolutionsAndServicesSerializer(many=True, read_only=True)
#     services_we_provide = ServicesWeProvideSerializer(many=True, read_only=True)
#     ecosystem = EcoSystemSerializer(many=True, read_only=True)
#     key_things = TechnologyKeyThingsSerializer(many=True, read_only=True)
#     tech_why_choose_us = TechnologyWhyChooseUsSerializer(many=True, read_only=True)
#     our_process = TechnologyOurProcessSerializer(many=True, read_only=True)
#     history_of_tech = HistoryOfTechSerializer(many=True, read_only=True)
#     faqs = TechnologyFAQSerializer(many=True, read_only=True)
#     faq_schema = TechnologyFAQSchemaSerializer(read_only=True)
#     ctas = TechnologyCTASerializer(many=True, read_only=True)
#     table_of_contents = serializers.SerializerMethodField()

#     def get_table_of_contents(self, obj):
#         toc = []
        
#         # Add section titles from Solutions and Services
#         for item in obj.solutions_and_services.all():
#             if item.section_title:
#                 toc.append(item.section_title)
        
#         # Add section titles from Services We Provide
#         for item in obj.services_we_provide.all():
#             if item.section_title:
#                 toc.append(item.section_title)
        
#         # Add section titles from EcoSystem
#         for item in obj.ecosystem.all():
#             if item.section_title:
#                 toc.append(item.section_title)
        
#         # Add section titles from Key Things
#         for item in obj.KeyThings.all():
#             if item.section_title:
#                 toc.append(item.section_title)
        
#         # Add section titles from Why Choose Us
#         for item in obj.Tech_why_choose_us.all():
#             if item.section_title:
#                 toc.append(item.section_title)
        
#         # Add section titles from Our Process
#         for item in obj.our_process.all():
#             if item.section_title:
#                 toc.append(item.section_title)
        
#         # Add section titles from History of Tech
#         for item in obj.history_of_tech.all():
#             if item.section_title:
#                 toc.append(item.section_title)
        
#         return toc

    
#     class Meta:
#         model = Technology
#         fields = '__all__'
#         ref_name = 'TechnologyDetailSerializer'

class TechnologyDetailSerializer(serializers.ModelSerializer):
    type = TechnologyTypeSerializer(read_only=True)
    solutions_and_services = TechnologySolutionsAndServicesSerializer(many=True, read_only=True)
    creators_quotes = TechnologyCreatorsQuotesSerializer(many=True, read_only=True)
    services_we_provide = ServicesWeProvideSerializer(many=True, read_only=True)
    ecosystem = EcoSystemSerializer(many=True, read_only=True)
    KeyThings = TechnologyKeyThingsSerializer(many=True, read_only=True)  # Changed from key_things
    why_choose_us = TechnologyWhyChooseUsSerializer(many=True, read_only=True, source='Tech_why_choose_us')  # Changed from tech_why_choose_us
    our_process = TechnologyOurProcessSerializer(many=True, read_only=True)
    history_of_tech = HistoryOfTechSerializer(many=True, read_only=True)
    faqs = TechnologyFAQSerializer(many=True, read_only=True)
    faq_schema = TechnologyFAQSchemaSerializer(read_only=True)
    ctas = TechnologyCTASerializer(many=True, read_only=True)
    table_of_contents = serializers.SerializerMethodField()
    
    def get_table_of_contents(self, obj):
        toc = []
        
        # Add section titles from Solutions and Services
        for item in obj.solutions_and_services.all():
            if item.section_title:
                toc.append(item.section_title)
        
        # Add section titles from Services We Provide
        for item in obj.services_we_provide.all():
            if item.section_title:
                toc.append(item.section_title)
        
        # Add section titles from EcoSystem
        for item in obj.ecosystem.all():
            if item.section_title:
                toc.append(item.section_title)
        
        # Add section titles from Key Things
        for item in obj.KeyThings.all():  # Changed from key_things
            if item.section_title:
                toc.append(item.section_title)
        
        # Add section titles from Why Choose Us
        for item in obj.Tech_why_choose_us.all():  # Changed from tech_why_choose_us
            if item.section_title:
                toc.append(item.section_title)
        
        # Add section titles from Our Process
        for item in obj.our_process.all():
            if item.section_title:
                toc.append(item.section_title)
        
        # Add section titles from History of Tech
        for item in obj.history_of_tech.all():
            if item.section_title:
                toc.append(item.section_title)
        
        return toc
    
    class Meta:
        model = Technology
        fields = '__all__'
        ref_name = 'TechnologyDetailSerializer'




# ==================================== Additional Page Serializers ====================================


class AdditionalPageKeyThingsCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalPageKeyThingsCards
        fields = '__all__'
        ref_name = 'AdditionalPageKeyThingsCards'

class AdditionalPageKeyThingsSerializer(serializers.ModelSerializer):
    keyThings_cards = AdditionalPageKeyThingsCardsSerializer(many=True, read_only=True, source='additional_page_key_things_cards.all')
    
    class Meta:
        model = AdditionalPageKeyThings
        fields = '__all__'
        ref_name = 'AdditionalPageKeyThings'

class AdditionalPageHeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalPageHeroSection
        fields = '__all__'
        ref_name = 'AdditionalPageHeroSection'

class WhatIsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatIs
        fields = '__all__'
        ref_name = 'WhatIs'

class AdditionalPageWhyChooseUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalPageWhyChooseUs
        fields = '__all__'
        ref_name = 'AdditionalPageWhyChooseUs'

class AdditionalPageOurProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalPageOurProcess
        fields = '__all__'
        ref_name = 'AdditionalPageOurProcess'

class AdditionalPageFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalPageFAQ
        fields = '__all__'
        ref_name = 'AdditionalPageFAQ'

class TeamElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamElement
        fields = '__all__'
        ref_name = 'TeamElement'

class AdditionalPagesSerializer(serializers.ModelSerializer):
    hero_section = serializers.SerializerMethodField()
    what_is = serializers.SerializerMethodField()
    keyThings = serializers.SerializerMethodField()
    why_choose_us = serializers.SerializerMethodField()
    our_process = AdditionalPageOurProcessSerializer(many=True, read_only=True)
    faqs = AdditionalPageFAQSerializer(many=True, read_only=True)
    team_elements = TeamElementSerializer(many=True, read_only=True)
    
       
    class Meta:
        model = AdditionalPages
        fields = [
            'id', 'title', 'slug', 'description', 'created_at', 'updated_at',
            'hero_section', 'what_is', 'keyThings', 'why_choose_us', 
            'our_process', 'faqs', 'team_elements'
        ]
        ref_name = 'AdditionalPages'
    
    def get_hero_section(self, obj):
        try:
            section = obj.additional_page_hero_section.first()
            if section:
                return AdditionalPageHeroSectionSerializer(section).data
        except Exception:
            pass
        return None
    
    def get_what_is(self, obj):
        try:
            what_is = obj.what_is_next.first()
            if what_is:
                return WhatIsSerializer(what_is).data
        except Exception:
            pass
        return None
    
    def get_keyThings(self, obj):
        try:
            key_things = obj.additional_page_key_things.first()
            if key_things:
                return [AdditionalPageKeyThingsSerializer(key_things).data]
        except Exception:
            pass
        return None
    
    def get_why_choose_us(self, obj):
        try:
            why_choose = obj.additional_page_why_choose_us.first()
            if why_choose:
                return AdditionalPageWhyChooseUsSerializer(why_choose).data
        except Exception:
            pass
        return None
    
    def get_team_elements(self, obj):
        try:
            team_elements = obj.team_elements.all()
            if team_elements:
                return TeamElementSerializer(team_elements, many=True).data
        except Exception:
            pass
        return None
    





# ===================================== Award Serializers ======================================

class AwardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Awards
        # fields = ['title', 'image_url', 'description']
        fields = '__all__'
        ref_name = 'CategoryAward'

class AwardYearGroupSerializer(serializers.ModelSerializer):
    awards = AwardsSerializer(many=True, read_only=True)
    
    class Meta:
        model = AwardYearGroup
        fields = ['year', 'awards']
        ref_name = 'CategoryYearGroup'

class AwardCategorySerializer(serializers.ModelSerializer):
    awards = AwardYearGroupSerializer(source='year_groups', many=True, read_only=True)
    
    class Meta:
        model = AwardCategory
        fields = ['id', 'section_title', 'section_description', 'awards']
        ref_name = 'AwardCategoryDetail'
        
class AwardCategoryListResponseSerializer(serializers.Serializer):
    table_of_content = serializers.ListField(child=serializers.CharField())
    categories = AwardCategorySerializer(many=True)


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'
        ref_name = 'CertificationSerializer'