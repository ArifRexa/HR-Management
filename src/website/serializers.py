from rest_framework import serializers

from employee.models import (
    Employee,
    EmployeeSocial,
    EmployeeContent,
    EmployeeNOC,
)
from project_management.models import (
    Project,
    Client,
    Technology,
    ProjectTechnology,
    ProjectContent,
    ProjectScreenshot,
    Tag,
)
from website.models import (
    Service,
    Blog,
    Category,
    BlogTag,
    BlogCategory,
    BlogContext,
)


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ("icon", "name")


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("name", "email", "address", "country", "logo")


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("title", "slug", "icon", "short_description")


class ServiceDetailsSerializer(serializers.ModelSerializer):
    clients = ClientSerializer(many=True)
    technologies = TechnologySerializer(many=True)

    class Meta:
        model = Service
        fields = "__all__"


class ProjectTechnologySerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True)

    class Meta:
        model = ProjectTechnology
        fields = ("title", "technologies")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name",)


class ProjectSerializer(serializers.ModelSerializer):
    technologies = ProjectTechnologySerializer(
        many=True, source="projecttechnology_set"
    )
    available_tags = TagSerializer(read_only=True, many=True, source="tags")

    class Meta:
        model = Project
        fields = (
            "title",
            "slug",
            "description",
            "thumbnail",
            "video_url",
            "technologies",
            "available_tags",
        )


class ProjectContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectContent
        fields = ("title", "content")


class ProjectScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectScreenshot
        fields = ("image",)


class ProjectDetailsSerializer(serializers.ModelSerializer):
    technologies = ProjectTechnologySerializer(
        source="projecttechnology_set", many=True, read_only=True
    )
    contents = ProjectContentSerializer(
        source="projectcontent_set", many=True, read_only=True
    )
    screenshots = ProjectScreenshotSerializer(
        source="projectscreenshot_set", many=True, read_only=True
    )

    class Meta:
        model = Project
        fields = (
            "title",
            "slug",
            "description",
            "thumbnail",
            "video_url",
            "tags",
            "technologies",
            "contents",
            "screenshots",
        )


class EmployeeSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSocial
        fields = ("title", "url")


class EmployeeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeContent
        fields = ("title", "content")


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


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


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
        fields = ("full_name", "image")


class BlogContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogContext
        fields = ["id", "title", "description"]


class BlogListSerializer(serializers.ModelSerializer):
    # tags = BlogTagSerializer(many=True, source='blogtag_set')
    # categories = BlogCategoriesSerializer(many=True, source='blogcategory_set')
    category = serializers.SerializerMethodField("get_category")
    author = AuthorSerializer(source="created_by.employee")
    blog_contexts = BlogContextSerializer(many=True)

    class Meta:
        model = Blog
        fields = (
            "slug",
            "title",
            "short_description",
            "image",
            "category",
            "read_time_minute",
            "created_at",
            "author",
            "blog_contexts",
        )

    def get_category(self, instance):
        blogcategory = instance.blogcategory_set.first()
        if blogcategory:
            return blogcategory.category.name
        return "-"


class BlogDetailsSerializer(serializers.ModelSerializer):
    # tags = BlogTagSerializer(many=True, source='blogtag_set')
    # categories = BlogCategoriesSerializer(many=True, source='blogcategory_set')
    category = serializers.SerializerMethodField("get_category")
    author = AuthorSerializer(source="created_by.employee")

    class Meta:
        model = Blog
        fields = (
            "slug",
            "title",
            "short_description",
            "image",
            "category",
            "read_time_minute",
            "created_at",
            "author",
            "content",
        )

    def get_category(self, instance):
        blogcategory = instance.blogcategory_set.first()
        if blogcategory:
            return blogcategory.category.name
        return "-"


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
