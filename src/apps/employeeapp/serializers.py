import datetime
from calendar import month_abbr

from django.db.models import Case, FloatField, IntegerField, Q, Sum, When, functions
from django.utils import timezone
from rest_framework import serializers

from apps.authentication.serializers import UserSerializer
from apps.authentication.utils import get_week_date_range
from apps.mixin.serializer import BaseModelSerializer
from employee.models.attachment import Attachment
from employee.models.employee import Employee
from employee.models.employee_skill import EmployeeSkill
from employee.models.leave.leave import Leave


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


class EmployeeAttachmentSerializer(BaseModelSerializer):
    class Meta:
        model = Attachment
        fields = ["id", "file_name", "file"]
        ref_name = "api_employee_attachment"


class EmployeeSkillSerializer(BaseModelSerializer):
    skill = serializers.CharField(source="skill.title")

    class Meta:
        model = EmployeeSkill
        fields = ["skill", "percentage"]
        ref_name = "api_employee_skill"


class DashboardSerializer(BaseModelSerializer):
    designation = serializers.CharField(source="designation.title")
    employee_id = serializers.SerializerMethodField()
    attachments = EmployeeAttachmentSerializer(
        many=True, read_only=True, source="attachment_set"
    )
    skills = EmployeeSkillSerializer(
        many=True, read_only=True, source="employeeskill_set"
    )
    projects = serializers.SerializerMethodField()

    def get_projects(self, instance):
        return instance.employeeproject.project.filter(active=True).values_list(
            "title", flat=True
        )

    def get_employee_id(self, instance):
        return str(f"{instance.joining_date.strftime('%Y%d')}{instance.id}")

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "designation",
            "image",
            "joining_date",
            "employee_id",
            "attachments",
            "skills",
            "projects",
        ]
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

    def _get_leave_info(self, instance, _type: str = "casual"):
        current_year = timezone.now().year
        if _type == "medical":
            _type = ["medical", "half_day_medical"]
        elif _type == "casual":
            _type = ["casual", "half_day"]
        else:
            _type = ["non_paid"]
        passed_leave = (
            Leave.objects.annotate(
                leave_count=Case(
                    When(
                        Q(leave_type="medical")
                        | Q(leave_type="casual")
                        | Q(leave_type="non_paid") & Q(status="Approved"),
                        then=1,
                    ),
                    When(
                        Q(leave_type="half_day_medical")
                        | Q(leave_type="half_day") & Q(status="Approved"),
                        then=0.5,
                    ),
                    default=0,
                    output_field=FloatField(),
                )
            )
            .filter(employee=instance, end_date__year=current_year, leave_type__in=_type)
            .aggregate(total=Sum("leave_count"))
        )
        return passed_leave.get("total", 0)

    def _project_hour_statistic(self, instance):
        hour_data = (
            instance.employeeprojecthour_set.filter(
                created_at__year=timezone.now().year
            )
            .annotate(
                month=functions.ExtractMonth("created_at", output_field=IntegerField()),
            )
            .values("month")
            .annotate(total_hours=Sum("hours"))
            .order_by("month")
            .values("month", "total_hours")
        )
        hour_data = map(
            lambda x: {
                "month": month_abbr[x["month"]],
                "total_hours": x["total_hours"],
            },
            hour_data,
        )
        return hour_data

    def _late_fine_info(self, instance):
        current_date = timezone.now().date()
        last_month = current_date.replace(day=1) - timezone.timedelta(days=1)
        this_fine = (
            instance.lateattendancefine_set.filter(
                date__year=current_date.year,
                date__month=current_date.month,
                is_consider=False,
            ).count()
            * 80
        )
        last_fine = (
            instance.lateattendancefine_set.filter(
                date__year=last_month.year,
                date__month=last_month.month,
                is_consider=False,
            ).count()
            * 80
        )
        total_late_day = instance.employeeattendance_set.filter(
            date__year=current_date.year,
            date__month=current_date.month,
            entry_time__gt=datetime.time(11, 10),
        ).count()
        return {
            "this_month": this_fine,
            "last_month": last_fine,
            "total_late_day": total_late_day,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["project_hours"] = self._get_project_hour(instance)
        data["leave_info"] = {
            "passed_casual": self._get_leave_info(instance, "casual") or 0,
            "total_casual": instance.leave_management.casual_leave or 0,
            "passed_medical": self._get_leave_info(instance, "medical") or 0,
            "total_medical": instance.leave_management.medical_leave or 0,
            "passed_non_paid": self._get_leave_info(instance, "non_paid") or 0,
        }
        data["project_hour_statistic"] = self._project_hour_statistic(instance)
        data["late_fine_info"] = self._late_fine_info(instance)
        return data
