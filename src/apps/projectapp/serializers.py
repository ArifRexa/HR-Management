from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers
from django.db.models import Sum

from account.models import Income
from apps.employeeapp.serializers import EmployeeInfoSerializer
from apps.mixin.serializer import BaseModelSerializer
from employee.models.employee import Employee, EmployeeUnderTPM
from project_management.models import (
    Client,
    ClientInvoiceDate,
    ClientReview,
    Country,
    CurrencyType,
    DailyProjectUpdate,
    DailyProjectUpdateAttachment,
    DailyProjectUpdateHistory,
    EmployeeProjectHour,
    InvoiceType,
    PaymentMethod,
    Project,
    ProjectContent,
    ProjectHour,
    Teams,
)

class ProjectContentModelSerializer(BaseModelSerializer):

    class Meta:
        model = ProjectContent
        exclude = ["project", ]


class ProjectSerializer(BaseModelSerializer):
    projectcontent_set = ProjectContentModelSerializer(many=True, required=False)

    class Meta:
        model = Project
        fields = [
            "id", "title", "web_title", "slug", "description", "client",
            "client_web_name", "client_image", "client_review",
            "platforms", "industries", "services", "live_link",
            "location", "country", "active", "is_special",
            "hourly_rate", "activate_from", "featured_image", "display_image",
            "project_logo", "special_image", "thumbnail", "featured_video",
            "show_in_website", "tags", "is_highlighted",
            "is_team", "projectcontent_set"
        ]
        extra_kwargs = {
            "slug": {
                "read_only": True,
            }
        }
        ref_name = "api_project_serializer"
    
    def create(self, validated_data):
        """
        save the Project and related ProjectContent data and return the project instance.
        """
        project_contents = validated_data.pop("projectcontent_set", [])

        # build unique slug for same project name.
        projects = self.Meta.model.objects.filter(slug__contains=slugify(validated_data.get("title")))
        if projects.exists():
            validated_data['slug'] = slugify(validated_data.get("title")+ f" {projects.count()}")
        
        project = super().create(validated_data)
        
        project_contents_list = []
        for project_content in project_contents:
            project_contents_list.append(
                ProjectContent(
                    project=project,
                    **project_content,
                )
            )
        if project_contents_list:
            ProjectContent.objects.bulk_create(project_contents_list)
        return project


class DailyProjectUpdateAttachmentSerializer(BaseModelSerializer):
    attachment = serializers.FileField(required=True)

    class Meta:
        model = DailyProjectUpdateAttachment
        fields = ("title", "attachment")
        extra_kwargs = {"created_at": {"read_only": True}}


class DailyProjectUpdateHistorySerializer(BaseModelSerializer):
    class Meta:
        model = DailyProjectUpdateHistory
        exclude = ("daily_update", "created_by")


class DailyProjectUpdateListSerializer(serializers.ModelSerializer):
    employee = EmployeeInfoSerializer()
    manager = EmployeeInfoSerializer()
    history = DailyProjectUpdateHistorySerializer(
        many=True, read_only=True, required=False
    )

    class Meta:
        model = DailyProjectUpdate
        fields = (
            "id",
            "updates_json",
            "employee",
            "manager",
            "status",
            "hours",
            "history",
            "created_at",
        )


class DailyProjectUpdateCreateSerializer(BaseModelSerializer):
    attachment = DailyProjectUpdateAttachmentSerializer(many=True, required=False)
    # manager = serializers.PrimaryKeyRelatedField(
    #     queryset=Employee.objects.all()
    # )
    class Meta:
        model = DailyProjectUpdate
        ignore_exclude_fields = ["created_at"]
        fields = "__all__"
        extra_kwargs = {
            "hours": {"required": True, "write_only": True},
            "update": {"required": True, "write_only": True},
            "updates_json": {"read_only": True},
            "employee": {"read_only": True},
            "status": {"read_only": True},
            "created_at": {"read_only": True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get("request", None)
        # self.read_only_fields = ["employee", "status", "created_at", "note"]
        # self._get_readonly_fields(self.request, self.instance)

    def _get_readonly_fields(self, request, obj=None):
        if not request or not request.user:
            return
        if request.user.is_superuser or request.user.has_perm(
            "project_management.can_submit_previous_daily_project_update"
        ):
            return
        if request.user.has_perm(
            "project_management.can_approve_or_edit_daily_update_at_any_time"
        ):
            self.fields["created_at"].read_only = True
            return

        if not obj:
            for field in self.read_only_fields:
                self.fields[field].read_only = True
            return

        if obj:
            # If interact  as selected manager for that project
            if obj.manager == request.user.employee:
                # If interacts also as the employee and manager of that project
                if obj.employee == request.user.employee:
                    self.fields["created_at"].read_only = True
                    return

                # If not the employee
                for field in [
                    "created_at",
                    "employee",
                    "manager",
                    "project",
                    "update",
                    # "updates_json",
                ]:
                    self.fields[field].read_only = True
                return

            # If interact as the project employee and status approved
            if obj.employee == request.user.employee and obj.status == "approved":
                for field in self.get_fields(request):
                    self.fields[field].read_only = True
                return

            # If interact as the project employee and status not approved
            for field in self.read_only_fields:
                self.fields[field].read_only = True
            return

    def validate(self, attrs):
        if not self.partial:
            if self.request.user:
                employee = self.request.user.employee
            else:
                employee = self.instance.employee
            if DailyProjectUpdate.objects.filter(
                employee=employee,
                project=attrs.get("project"),
                manager=attrs.get("manager"),
                created_at__date=timezone.now().date(),
            ).exists():
                raise serializers.ValidationError(
                    "Already you have given today's update for this project"
                )
            attrs["employee"] = employee
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["updates_json"] = [
            [validated_data.pop("update", None), "0.00", ""]
        ]
        instance = super().create(validated_data)

        if self.partial:
            instance.history.create(hours=instance.hours)

        return instance


class DailyProjectUpdateSerializer(DailyProjectUpdateCreateSerializer):
    history = DailyProjectUpdateHistorySerializer(
        many=True, read_only=True, required=False
    )
    employee = EmployeeInfoSerializer()
    manager = EmployeeInfoSerializer()


    def _get_readonly_fields(self, request, obj=None):
        if not request or not request.user:
            return
        if request.user.is_superuser or request.user.has_perm(
            "project_management.can_submit_previous_daily_project_update"
        ):
            return
        if request.user.has_perm(
            "project_management.can_approve_or_edit_daily_update_at_any_time"
        ):
            self.fields["created_at"].read_only = True
            return

        if not obj:
            for field in self.read_only_fields:
                self.fields[field].read_only = True
            return

        if obj:
            # If interact  as selected manager for that project
            if obj.manager == request.user.employee:
                # If interacts also as the employee and manager of that project
                if obj.employee == request.user.employee:
                    self.fields["created_at"].read_only = True
                    return

                # If not the employee
                for field in [
                    "created_at",
                    "employee",
                    "manager",
                    "project",
                    "update",
                    # "updates_json",
                ]:
                    self.fields[field].read_only = True
                return

            # If interact as the project employee and status approved
            if obj.employee == request.user.employee and obj.status == "approved":
                for field in self.get_fields(request):
                    self.fields[field].read_only = True
                return

            # If interact as the project employee and status not approved
            for field in self.read_only_fields:
                self.fields[field].read_only = True
            return


    def update(self, instance, validated_data):
        if validated_data.get("update"):
            validated_data["updates_json"] = [
                [validated_data.pop("update", None), "0.00", ""]
            ]
        instance = super().update(instance, validated_data)
        if self.partial and not validated_data.get("hours", None):
            instance.history.create(hours=instance.hours)
        return instance


class BulkDailyUpdateSerializer(BaseModelSerializer):
    update_ids = serializers.ListField(
        required=True, child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = DailyProjectUpdate
        fields = ("update_ids",)


class StatusUpdateSerializer(BulkDailyUpdateSerializer):

    class Meta:
        model = DailyProjectUpdate
        fields = ("status", "update_ids")


class ProjectHourHistorySerializer(BaseModelSerializer):
    class Meta:
        model = DailyProjectUpdate
        fields = "__all__"


class EmployeeProjectHourSerializer(BaseModelSerializer):
    class Meta:
        model = EmployeeProjectHour
        exclude = ("project_hour",)


class WeeklyProjectUpdate(BaseModelSerializer):
    hour_history = ProjectHourHistorySerializer(
        source="projecthourhistry_set", read_only=True, many=True
    )
    employee_project_hour = EmployeeProjectHourSerializer(
        source="employeeprojecthour_set", many=True
    )

    class Meta:
        model = ProjectHour
        fields = "__all__"
        ref_name = "api_weekly_project_update"
        extra_kwargs = {"tpm": {"read_only": True}}

    def get_fields(self):
        """
        Dynamically adjust fields based on user permissions, mirroring the provided get_fields logic.
        """
        fields = super().get_fields()
        request = self.context.get("request", None)

        if request and not request.user.is_superuser:
            if "manager" in fields:
                del fields["manager"]
            if "payable" in fields:
                del fields["payable"]

            if not request.user.has_perm("project_management.select_hour_type"):
                if "hour_type" in fields:
                    del fields["hour_type"]

            if request.user.is_authenticated and not request.user.employee.is_tpm:
                if "status" in fields:
                    del fields["status"]

        return fields

    def create(self, validated_data):
        request = self.context["request"]
        project = validated_data.get("project")
        if (
            validated_data.get("hour_type") != "bonus"
            and project
            and ProjectHour.objects.filter(
                manager_id=request.user.employee.id,
                project_id=project.id,
                date=validated_data.get("date"),
            ).exists()
        ):
            raise serializers.ValidationError(
                {
                    "date": "Project Hour for this date with this project and manager already exists",
                }
            )

        request = self.context.get("request", None)
        validated_data["manager"] = request.user.employee
        employee_project_hour = validated_data.pop("employee_project_hour", None)
        employee_hour_list = []
        tpm_project = EmployeeUnderTPM.objects.select_related("tpm").filter(
            project=validated_data.get("project")
        )
        if tpm_project.exists():
            validated_data["tpm"] = tpm_project.first().tpm
        else:
            validated_data["status"] = "approved"

        instance = super().create(validated_data)
        if employee_project_hour:
            employee_hour_list.append(
                EmployeeProjectHour(**employee_project_hour, project_hour=instance)
            )

        EmployeeProjectHour.objects.select_related("employee").bulk_create(
            employee_hour_list
        )
        return instance

    def update(self, instance, validated_data):
        request = self.context.get("request", None)
        seven_day_earlier = timezone.now() - timezone.timedelta(days=6)
        if (
            instance.created_at <= seven_day_earlier
            and not request.user.is_superuser
            and not request.user.has_perm(
                "project_management.weekly_project_hours_approve"
            )
        ):
            raise serializers.ValidationError(
                "Cannot update project hours older than 6 days unless you are a superuser or have approval permission."
            )
        if (
            request.user.employee.is_tpm
            and not EmployeeUnderTPM.objects.filter(
                tpm=request.user.employee, project=instance.project
            ).exists()
        ):
            raise serializers.ValidationError("You are not assign TPM for this project")
        employee_project_hour = validated_data.pop("employee_project_hour", None)

        instance = super().update(instance, validated_data)

        if employee_project_hour:

            existing_hour = (
                EmployeeProjectHour.objects.select_related("employee")
                .filter(project_hour=instance)
                .first()
            )
            if existing_hour:

                for key, value in employee_project_hour.items():
                    setattr(existing_hour, key, value)
                existing_hour.save()
            else:
                EmployeeProjectHour.objects.select_related("employee").create(
                    **employee_project_hour, project_hour=instance
                )

        return instance


class BulkUpdateSerializer(serializers.Serializer):
    ids = serializers.ListField(
        required=True, child=serializers.IntegerField(), write_only=True
    )


class IncomeSerializer(BaseModelSerializer):
    class Meta:
        model = Income
        fields = "__all__"
        ref_name = "api_income"


class ProjectResourceModelSerializer(BaseModelSerializer):
    employees = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = [
            "id", "title", "employees",
        ]
    
    def get_employees(self, instance):
        employee_projects = getattr(instance, "employeeprojects", [])
        return  EmployeeInfoSerializer(
            instance=[employee_project.employee for employee_project in employee_projects],
            many=True,
            context={"request": self.context.get("request")}
        ).data


class ProjectResourceAddDeleteSerializer(serializers.Serializer):
    employee_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Employee.objects.all()
    )
    project_id = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Project.objects.filter(active=True).all()
    )
    

class ClientInvoiceDateBaseModelSerializer(BaseModelSerializer):

    class Meta:
        model = ClientInvoiceDate
        exclude = ["clients"]


class ClientInvoiceDateModelSerializer(ClientInvoiceDateBaseModelSerializer):
    id = serializers.IntegerField()


class CountryModelSerializer(BaseModelSerializer):

    class Meta:
        model = Country
        fields = "__all__"


class PaymentMethodModelSerializer(BaseModelSerializer):

    class Meta:
        model = PaymentMethod
        fields = "__all__"


class InvoiceTypeModelSerializer(BaseModelSerializer):

    class Meta:
        model = InvoiceType
        fields = "__all__"


class ClientReviewModelSerializer(BaseModelSerializer):

    class Meta:
        model = ClientReview
        fields = "__all__"



class CurrencyTypeModelSerializer(BaseModelSerializer):

    class Meta:
        model = CurrencyType
        exclude = [
            "is_active", "is_default", "exchange_rate"
        ]


class ClientBaseModelSerializer(BaseModelSerializer):
    clientinvoicedate_set = ClientInvoiceDateBaseModelSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Client
        fields = "__all__"

    def create(self, validated_data):
        clientinvoicedate_set = validated_data.pop("clientinvoicedate_set", [])
        client = super().create(validated_data)
        client_invoice_date_list = []
        for client_invoice_date in clientinvoicedate_set:
            client_invoice_date_list.append(
                ClientInvoiceDate(
                    clients=client,
                    **client_invoice_date,
                )
            )
        if client_invoice_date_list:
            ClientInvoiceDate.objects.bulk_create(client_invoice_date_list)
        return client

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["country"] = CountryModelSerializer(instance=instance.country).data
        representation["payment_method"] = PaymentMethodModelSerializer(instance=instance.payment_method).data
        representation["invoice_type"] = InvoiceTypeModelSerializer(instance=instance.invoice_type).data
        representation["review"] = ClientReviewModelSerializer(
            instance=instance.review.all(),
            many=True,
        ).data
        representation["currency"] = CurrencyTypeModelSerializer(instance=instance.currency).data
        return representation



class ClientModelSerializer(ClientBaseModelSerializer):
    clientinvoicedate_set = ClientInvoiceDateModelSerializer(
        many=True,
        required=False,
    )

    def update(self, instance, validated_data):
        review = validated_data.pop("review", [])
        if review:
            instance.review.set(review)
        
        clientinvoicedate_set = validated_data.pop("clientinvoicedate_set", [])
        if clientinvoicedate_set:
            client_invoice_dates = ClientInvoiceDate.objects.filter(
                clients_id=instance.id,
                id__in=[client_invoice_date.get("id") for client_invoice_date in clientinvoicedate_set]
            )
            for client_invoice_date_obj, client_invoice_date_dict in zip(client_invoice_dates, clientinvoicedate_set):
                client_invoice_date_obj.invoice_date = client_invoice_date_dict.get("invoice_date")
            ClientInvoiceDate.objects.bulk_update(client_invoice_dates, fields=["invoice_date"])
            
        return super().update(instance, validated_data)
    

class TeamProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'slug', 'description', 'active']
        read_only_fields = ['id', 'slug']


class EmployeeSerializer(serializers.ModelSerializer):
    designation = serializers.CharField(source='designation.name', read_only=True, allow_null=True)

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'email', 'designation', 'active']
        read_only_fields = ['id', 'full_name', 'email', 'designation', 'active']
        ref_name = 'api_employee_serializer'

class TeamSerializer(serializers.ModelSerializer):
    projects = TeamProjectSerializer(many=True, read_only=True)
    employees = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = Teams
        # fields = ['id', 'team_name', 'description', 'team_image', 'projects', 'employees', 'created_at', 'updated_at']
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_team_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Team name cannot be empty.')
        if Teams.objects.filter(team_name__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError('Team name must be unique.')
        return value


class TeamUpdateSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(required=False, allow_blank=True)  # Make team_name optional
    description = serializers.CharField(required=False, allow_blank=True)  # Optional
    team_image = serializers.ImageField(required=False, allow_null=True)  # Optional for file uploads

    class Meta:
        model = Teams
        fields = ['id', 'team_name', 'description', 'team_image']
        read_only_fields = ['id']
        ref_name = 'api_team_update_serializer'

    def validate_team_name(self, value):
        value = value.strip()
        if value:  # Only validate if team_name is provided
            if Teams.objects.filter(team_name__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise serializers.ValidationError('Team name must be unique.')
        return value
    

class AddProjectsSerializer(serializers.Serializer):
    project_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        required=True
    )

    def validate_project_ids(self, value):
        projects = Project.objects.filter(id__in=value, active=True)
        if not projects.exists():
            raise serializers.ValidationError('No valid projects found for the provided IDs.')
        if len(projects) != len(set(value)):
            raise serializers.ValidationError('Some project IDs are invalid or duplicated.')
        return value

    class Meta:
        ref_name = 'api_add_projects_serializer'

class AddEmployeesSerializer(serializers.Serializer):
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        required=True
    )

    def validate_employee_ids(self, value):
        employees = Employee.objects.filter(id__in=value, active=True, project_eligibility=True)
        if not employees.exists():
            raise serializers.ValidationError('No valid employees found for the provided IDs.')
        if len(employees) != len(set(value)):
            raise serializers.ValidationError('Some employee IDs are invalid or duplicated.')
        return value

    class Meta:
        ref_name = 'api_add_employees_serializer'


class UpdateSerializer(serializers.ModelSerializer):
    """Serialize DailyProjectUpdate with update text from updates_json or update field."""
    update = serializers.SerializerMethodField()

    class Meta:
        model = DailyProjectUpdate
        fields = ['id', 'hours', 'update', 'status', 'created_at']

    def get_update(self, obj):
        """Return formatted updates_json if available, else fall back to update field."""
        return obj.str_updates_json if obj.updates_json else obj.update or ""

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """Serialize Employee with their updates and total hours for a project in a date range."""
    id = serializers.IntegerField(source='pk')
    total_hour = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'total_hour', 'updates']

    def get_updates(self, obj):
        """Fetch updates for the employee within the specified project and date range."""
        project_id = self.context['project_id']
        week_start = self.context['week_start']
        selected_date = self.context['selected_date']
        
        updates = obj.dailyprojectupdate_employee.filter(
            project_id=project_id,
            created_at__date__gte=week_start,
            created_at__date__lte=selected_date
        ).order_by('-created_at')
        
        return UpdateSerializer(updates, many=True).data

    def get_total_hour(self, obj):
        """Calculate total hours for the employee in the project and date range."""
        project_id = self.context['project_id']
        week_start = self.context['week_start']
        selected_date = self.context['selected_date']
        
        total_hours = obj.dailyprojectupdate_employee.filter(
            project_id=project_id,
            created_at__date__gte=week_start,
            created_at__date__lte=selected_date
        ).aggregate(total=Sum('hours'))['total'] or 0.0
        
        return f"{total_hours:.2f}"

class ProjectUpdateSerializer(serializers.Serializer):
    """Serialize project updates with manager name, total approved hours, and employee details."""
    manager = serializers.SerializerMethodField()
    lead = serializers.SerializerMethodField()
    total_approved_hour = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()

    def get_manager(self, obj):
        """Retrieve the project manager's full name from EmployeeUnderTPM."""
        tpm = EmployeeUnderTPM.objects.filter(project_id=obj['project_id']).select_related('tpm').first()
        # Fetch the lead who approved the latest daily project update for this project
        approved_update = DailyProjectUpdate.objects.filter(
            project_id=obj['project_id'],
            status='approved'
        ).select_related('manager').order_by('-created_at').first()
        
        lead_name = approved_update.manager.full_name if approved_update and approved_update.manager else "No Lead Assigned"
        print("Lead is:", lead_name, "\nManager is:", tpm.tpm.full_name)
        return tpm.tpm.full_name if tpm else "No Manager Assigned"
    
    def get_lead(self, obj):
        # Fetch the lead who approved the latest daily project update for this project
        approved_update = DailyProjectUpdate.objects.filter(
            project_id=obj['project_id'],
            status='approved'
        ).select_related('manager').order_by('-created_at').first()
        
        lead_name = approved_update.manager.full_name if approved_update and approved_update.manager else "No Lead Assigned"
        print("Lead is:", lead_name)
        return lead_name


    def get_total_approved_hour(self, obj):
        """Calculate total approved hours for the project in the date range."""
        total_approved = DailyProjectUpdate.objects.filter(
            project_id=obj['project_id'],
            created_at__date__gte=obj['week_start'],
            created_at__date__lte=obj['selected_date'],
            status='approved'
        ).aggregate(total=Sum('hours'))['total'] or 0.0
        
        return f"{total_approved:.0f}"

    def get_employees(self, obj):
        """Fetch employees with updates for the project in the date range."""
        employees = Employee.objects.filter(
            dailyprojectupdate_employee__project_id=obj['project_id'],
            dailyprojectupdate_employee__created_at__date__gte=obj['week_start'],
            dailyprojectupdate_employee__created_at__date__lte=obj['selected_date']
        ).distinct().prefetch_related('dailyprojectupdate_employee')
        
        return EmployeeUpdateSerializer(
            employees,
            many=True,
            context={
                'project_id': obj['project_id'],
                'week_start': obj['week_start'],
                'selected_date': obj['selected_date']
            }
        ).data

    class Meta:
        fields = ['manager', 'total_approved_hour', 'employees']

class ProjectUpdateFilterSerializer(serializers.Serializer):
    """Validate input parameters for project ID and selected date."""
    project_id = serializers.IntegerField(required=True, help_text="ID of the project to filter updates")
    selected_date = serializers.DateField(required=True, help_text="Date up to which updates are retrieved (YYYY-MM-DD)")

    def validate_selected_date(self, value):
        """Ensure the selected date is not in the future."""
        if value > timezone.now().date():
            raise serializers.ValidationError("Selected date cannot be in the future.")
        return value