from rest_framework import serializers

from employee.models import Employee, EmployeeSocial, EmployeeContent
from project_management.models import Project, Client, Technology, ProjectTechnology, ProjectContent, ProjectScreenshot
from website.models import Service


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ('icon', 'name')


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('name', 'email', 'address', 'country', 'logo')


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('title', 'slug', 'icon', 'short_description')


class ServiceDetailsSerializer(serializers.ModelSerializer):
    clients = ClientSerializer(many=True)
    technologies = TechnologySerializer(many=True)

    class Meta:
        model = Service
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('title', 'slug', 'description', 'thumbnail', 'video_url')


class ProjectTechnologySerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True)

    class Meta:
        model = ProjectTechnology
        fields = ('title', 'technologies')


class ProjectContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectContent
        fields = ('title', 'content')


class ProjectScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectScreenshot
        fields = ('image',)


class ProjectDetailsSerializer(serializers.ModelSerializer):
    technologies = ProjectTechnologySerializer(source='projecttechnology_set', many=True, read_only=True)
    contents = ProjectContentSerializer(source='projectcontent_set', many=True, read_only=True)
    screenshots = ProjectScreenshotSerializer(source='projectscreenshot_set', many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('title', 'slug', 'description', 'thumbnail', 'video_url', 'technologies', 'contents', 'screenshots')


class EmployeeSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSocial
        fields = ('title', 'url')


class EmployeeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeContent
        fields = ('title', 'content')


class EmployeeDetailsSerializer(serializers.ModelSerializer):
    designation = serializers.StringRelatedField(many=False)
    socials = EmployeeSocialSerializer(many=True, read_only=True, source='employeesocial_set')
    contents = EmployeeContentSerializer(many=True, read_only=True, source='employeecontent_set')

    class Meta:
        model = Employee
        fields = ('slug', 'full_name', 'joining_date', 'permanent_date', 'designation',
                  'manager', 'image', 'socials', 'contents')


class EmployeeSerializer(serializers.ModelSerializer):
    designation = serializers.StringRelatedField(many=False)
    socials = EmployeeSocialSerializer(many=True, read_only=True, source='employeesocial_set')

    class Meta:
        model = Employee
        fields = ('slug', 'full_name', 'designation', 'manager', 'image', 'socials')

    def get_image_url(self, employee):
        request = self.context.get('request')
        image_url = employee.image.url
        return request.build_absolute_uri(image_url)
