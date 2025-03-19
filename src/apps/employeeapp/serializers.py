from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import serializers

from apps.authentication.serializers import UserSerializer
from apps.authentication.utils import get_week_date_range
from apps.mixin.serializer import BaseModelSerializer
from employee.models.employee import Employee


class EmployeeListSerializer(BaseModelSerializer):
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj):
        return obj.user.get_all_permissions()

    class Meta:
        model = Employee
        fields = ["id", "full_name", "designation", "permissions", "image"]
        ref_name = "api_employee_list"


class EmployeeSerializer(BaseModelSerializer):
    user = UserSerializer(read_only=True)
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj):
        return obj.user.get_all_permissions()

    class Meta:
        model = Employee
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True},
        }
        ref_name = "api_employee"


class DashboardSerializer(BaseModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "full_name", "designation", "image"]
        ref_name = "api_dashboard"

    def _get_project_hour(self, instance):
        """_get_project_hour this function return employee last two week project hours

        Args:
            instance (Employee): _description_

        Returns:
            dict: {
                "this_week": 0,
                "last_week":23,
                "weekly_expected": 25
            }
        """
        this_week = get_week_date_range()
        last_week = get_week_date_range(week_number=2)
        project_hours = instance.employeeprojecthour_set.filter(
            created_at__date__gte=timezone.now().date() - timezone.timedelta(days=14)
        ).aggregate(
            this_week_h=Sum("hours", filter=Q(created_at__date__range=this_week)),
            last_week_h=Sum("hours", filter=Q(created_at__date__range=last_week)),
        )
        weekly_expected_hour = (
            int(instance.monthly_expected_hours / 4)
            if instance.monthly_expected_hours
            else 0
        )
        return {
            "this_week": project_hours.get("this_week_h") if project_hours else 0,
            "last_week": project_hours.get("last_week_h") if project_hours else 0,
            "weekly_expected": weekly_expected_hour,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["project_hours"] = self._get_project_hour(instance)
        return data
