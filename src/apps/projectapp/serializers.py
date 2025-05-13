from django.utils import timezone
from rest_framework import serializers

from account.models import Income
from apps.employeeapp.serializers import EmployeeInfoSerializer
from apps.mixin.serializer import BaseModelSerializer
from employee.models.employee import EmployeeUnderTPM
from project_management.models import (
    DailyProjectUpdate,
    DailyProjectUpdateAttachment,
    DailyProjectUpdateHistory,
    EmployeeProjectHour,
    Project,
    ProjectHour,
)


class ProjectSerializer(BaseModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"
        ref_name = "api_project_serializer"


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


class DailyProjectUpdateSerializer(BaseModelSerializer):
    attachment = DailyProjectUpdateAttachmentSerializer(many=True, required=False)
    history = DailyProjectUpdateHistorySerializer(
        many=True, read_only=True, required=False
    )
    employee = EmployeeInfoSerializer()
    manager = EmployeeInfoSerializer()
    class Meta:
        model = DailyProjectUpdate
        ignore_exclude_fields = ["created_at"]
        fields = "__all__"
        extra_kwargs = {
            "hours": {"required": True, "write_only": True},
            "update": {"required": True, "write_only": True},
            "updates_json": {"read_only": True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get("request", None)
        self.read_only_fields = ["employee", "status", "created_at", "note"]
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
            if attrs.get("employee"):
                employee = attrs.get("employee")
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

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["updates_json"] = [
            [validated_data.pop("update", None), "0.00", ""]
        ]
        instance = super().create(validated_data)

        if self.partial:
            instance.history.create(hours=instance.hours)

        return instance

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
