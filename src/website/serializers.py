from rest_framework import serializers

from employee.models import (
    Employee,
    EmployeeSocial,
    EmployeeContent,
    EmployeeNOC, Skill, EmployeeSkill,EmployeeExpertTech
)
from project_management.models import (
    Project,
    Client,
    Technology,
    ProjectTechnology,
    ProjectContent,
    ProjectScreenshot,
    Tag,
    ProjectOverview,
    ProjectStatement,
    ProjectChallenges,
    ProjectSolution,
    ProjectKeyFeature,
    ClientFeedback,
    ProjectResults,
    OurTechnology,
    ProjectPlatform,
    ProjectIndustry, 
    ProjectService,
    
    
    
    

)
from settings.models import Designation
from website.models import (
    Award,
    Gallery,
    Service,
    Blog,
    Category,
    BlogTag,
    BlogCategory,
    BlogContext,
    BlogComment,
    FAQ,
    ServiceProcess,
    OurAchievement,
    OurJourney,
    OurGrowth,
    EmployeePerspective,
    Industry,
    Lead,
)


class ProjectPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlatform
        fields = ('title',)

class ProjectIndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectIndustry
        fields = ('title',)

class ProjectServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectService
        fields = ('title',)


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ("icon", "name")

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("name", "email","designation", "address", "country", "logo","client_feedback")

class OurClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("name", "designation", "logo","client_feedback")




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
    technologies = ServiceTechnologySerializer(many=True, source="servicetechnology_set")
    industry = IndustrySerializer(many=True) 
    class Meta:
        model = Service
        fields = ("title", "slug","short_description","feature","technologies","industry","feature_image")




class ServiceDetailsSerializer(serializers.ModelSerializer):
    clients = ClientSerializer(many=True)
    technologies = ServiceTechnologySerializer(many=True, source="servicetechnology_set")
    service_process = ServiceProcessSerializer(many=True)
    class Meta:
        model = Service
        fields = ("slug","title","short_description","banner_image","feature_image","feature","service_process","technologies","clients")


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
        return Project.objects.filter(tags=obj,show_in_website=True).count()

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
            "feedback_week",
            "feedback",
            "avg_rating",
            "rating_communication",
            "rating_output",
            "rating_time_management",
            "rating_billing",
            "rating_long_term_interest",
        )


class ProjectKeyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectKeyFeature
        fields = ("title","description","img","img2")



class ProjectResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectResults
        fields = (
            "title",
            "increased_sales",
            "return_on_investment",
            "increased_order_rate",
        )

class ProjectSerializer(serializers.ModelSerializer):
    technologies = ProjectTechnologySerializer(many=True, source="projecttechnology_set")
    project_results = ProjectResultsSerializer() 
    industries = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "title",
            "slug",
            "description",
            "industries",
            "featured_image",
            "project_results",
            "technologies",
        )

    def get_industries(self, obj):

        return [industry.title for industry in obj.industries.all()]

class ProjectContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectContent
        fields = ("title", "content","image","image2")



class ProjectDetailsSerializer(serializers.ModelSerializer):
    technologies = ProjectTechnologySerializer(many=True, source="projecttechnology_set")
    available_tags = TagSerializer(read_only=True, many=True, source="tags")
    client = ClientSerializer()
    client_feedback = ProjectClientFeedbackSerializer(many=True, source="clientfeedback_set") 
    project_design = ProjectScreenshotSerializer(
        source="projectscreenshot_set", many=True, read_only=True
    )
    project_contents = ProjectContentSerializer(many=True, source="projectcontent_set")
    project_key_feature = ProjectKeyFeatureSerializer(many=True,source="projectkeyfeature_set")
    project_results = ProjectResultsSerializer() 
    platforms = ProjectPlatformSerializer(many=True)
    industries = ProjectIndustrySerializer(many=True)
    services = ProjectServiceSerializer(many=True)
    
    class Meta:
        model = Project
        fields = (
            "title",
            "slug",
            "platforms",
            "industries",
            "live_link",
            "location",
            "services",
            "project_results",
            "description",
            "featured_image",
            "featured_video",
            "technologies",
            "available_tags",
            "project_contents",
            "project_key_feature",
            "client",
            "client_feedback",
            "project_design",
        )
        


class ProjectHighlightedSerializer(serializers.ModelSerializer):
    
    project_results = ProjectResultsSerializer() 
    technologies = ProjectTechnologySerializer(many=True, source="projecttechnology_set")
    
    class Meta:
        model = Project
        fields = ("slug","title","description","project_results","thumbnail","technologies")

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
        fields = ['id','title', 'employee_count']

    def get_employee_count(self, obj):
        return Employee.objects.filter(designation=obj,active=True, show_in_web=True).count()

# class EmployeeSkillSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EmployeeSkill
#         fields = ['employee']


class SkillSerializer(serializers.ModelSerializer):
    total_employees = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ['id', 'title', 'total_employees']

    def get_total_employees(self, obj):
        return Employee.objects.filter(employeeskill__skill=obj,active=True, show_in_web=True).count()


class EmployeeSerializer(serializers.ModelSerializer):
    designation = serializers.SerializerMethodField()
    employeeskill = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'designation', 'image','operation', 'employeeskill']

    def get_designation(self, obj):
        if obj.designation:
            return obj.designation.title
        else:
            return None

    def get_employeeskill(self, obj):
        skills = EmployeeSkill.objects.filter(employee=obj)
        return [{'skill': skill.skill.title, 'percentage': skill.percentage} for skill in skills]

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
    class Meta:
        model = Employee
        fields = ("id", "full_name", "image")


class BlogContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogContext
        fields = ["id", "title", "description", "image", "video"]


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
            "short_description",
            "image",
            "category",
            "read_time_minute",
            "total_view",
            "created_at",
            "author",
            'blog_contexts'
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


class BlogDetailsSerializer(BlogListSerializer):
    tags = TagSerializer(many=True, source="tag")
    blog_contexts = BlogContextSerializer(many=True)

    class Meta(BlogListSerializer.Meta):
        fields = (
            "id",
            "slug",
            "title",
            "short_description",
            "image",
            "category",
            "tags",
            "read_time_minute",
            "created_at",
            "author",
            "content",
            "blog_contexts",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["total_blogs"] = instance.created_by.website_blog_related.filter(
            active=True
        ).count()
        data["total_comments"] = instance.comments.count()
        data["table_of_contents"] = instance.blog_contexts.all().values("id", "title")
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
        fields = ('title', 'technologies') 


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("question","answer")
   


class OurClientsFeedbackSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    client_designation = serializers.SerializerMethodField()
    client_logo = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('client_name', 'client_designation', 'client_logo', 'feedback')

    def get_client_name(self, obj):
        return obj.client.name if obj.client else None

    def get_client_designation(self, obj):
        return obj.client.designation if obj.client else None

    def get_client_logo(self, obj):
        if obj.client and obj.client.logo:
            return self.context['request'].build_absolute_uri(obj.client.logo.url)
        return None

    def get_feedback(self, obj):
        clientfeedback = ClientFeedback.objects.filter(project=obj)
        serializers = ClientFeedbackSerializer(instance=clientfeedback, many=True)
        return serializers.data
    

class OurAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurAchievement
        fields = ("title","number")


class OurGrowthSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurGrowth
        fields = ("title","number")

    

class OurJourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = OurJourney
        fields = ("year","title","description","img")


class EmployeePerspectiveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name',read_only =True)
    employee_designation = serializers.CharField(source='employee.designation',read_only=True)
    employee_image= serializers.ImageField(source='employee.image',read_only=True)
    class Meta:
        model = EmployeePerspective
        fields = ("title","description","employee_name","employee_designation","employee_image",)


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['name', 'email', 'message']
        

class ClientLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['logo']
        
class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['image']
        

class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ['image']
        

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['name', 'designation', 'image', 'client_feedback']