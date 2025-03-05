from django.utils import timezone
from rest_framework import serializers

from apps.mixin.serializer import BaseModelSerializer
from employee.models.employee import EmployeeUnderTPM
from project_management.models import (
    DailyProjectUpdate,
    DailyProjectUpdateAttachment,
    ProjectHour,
)


class DailyProjectUpdateAttachmentSerializer(BaseModelSerializer):
    attachment = serializers.FileField(required=True)

    class Meta:
        model = DailyProjectUpdateAttachment
        fields = ("title", "attachment")
        extra_kwargs = {"created_at": {"read_only": True}}


class DailyProjectUpdateCreateSerializer(BaseModelSerializer):
    attachment = DailyProjectUpdateAttachmentSerializer(many=True, required=False)

    class Meta:
        model = DailyProjectUpdate
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


class WeeklyProjectUpdate(BaseModelSerializer):

    class Meta:
        model = ProjectHour
        fields = "__all__"
        ref_name = "api_weekly_project_update"

    def create(self, validated_data):
        request = self.context.get("request", None)
        validated_data["manager"] = request.user.employee

        tpm_project = EmployeeUnderTPM.objects.select_related("employee", "tpm").filter(
            project=validated_data.get("project")
        )
        if tpm_project.exists():
            validated_data["tpm"] = tpm_project.first().tpm
        else:
            validated_data["status"] = "approved"

        super().create(validated_data)
