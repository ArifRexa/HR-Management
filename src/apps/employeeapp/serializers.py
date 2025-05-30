import datetime
from calendar import month_abbr

from django.db.models import (
    Case,
    DurationField,
    ExpressionWrapper,
    F,
    FloatField,
    Q,
    Sum,
    When,
    functions,
)
from django.utils import timezone
from rest_framework import serializers

from apps.authentication.serializers import UserSerializer
from apps.authentication.utils import get_week_date_range
from apps.mixin.serializer import BaseModelSerializer
from employee.models.attachment import Attachment
from employee.models.employee import Employee
from employee.models.employee_activity import EmployeeActivity
from employee.models.employee_skill import EmployeeSkill
from employee.models.leave.leave import Leave


class EmployeeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "full_name", "designation","image"]
        ref_name = "api_employee_info"

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
    designation = serializers.CharField(source="designation.title")
    skill = serializers.SerializerMethodField(method_name="get_skill")
    
    def get_skill(self, obj):
        employee_skill = getattr(obj, "top_one_skill", None)
        if employee_skill:
            return employee_skill.skill.title
        
        return None
    
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


from django.db.models import Func


class ExtractEpoch(Func):
    function = "TIMESTAMPDIFF"
    template = "%(function)s(SECOND, %(expressions)s)"
    output_field = FloatField()

    def __init__(self, start_time, end_time, **extra):
        expressions = (start_time, end_time)
        super().__init__(*expressions, **extra)


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

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "designation",
            "image",
            "joining_date",
            "permanent_date",
            "employee_id",
            "attachments",
            "skills",
            "projects",
        ]
        ref_name = "api_dashboard"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cache frequently used values
        self.current_date = timezone.now().date()
        self.current_year = self.current_date.year
        self.last_month = self.current_date.replace(day=1) - timezone.timedelta(days=1)
        self.this_week = get_week_date_range()
        self.last_week = get_week_date_range(2)

    def get_projects(self, instance):
        return instance.employeeproject.project.filter(active=True).values_list(
            "title", flat=True
        )

    def get_employee_id(self, instance):
        return f"{instance.joining_date.strftime('%Y%d')}{instance.id}"

    def _get_project_hour(self, instance):
        fourteen_days_ago = self.current_date - timezone.timedelta(days=14)
        project_hours = instance.employeeprojecthour_set.filter(
            created_at__date__gte=fourteen_days_ago
        ).aggregate(
            this_week_h=Sum(
                "hours", filter=Q(project_hour__date__range=self.this_week)
            ),
            last_week_h=Sum(
                "hours", filter=Q(project_hour__date__range=self.last_week)
            ),
        )

        weekly_expected = (
            instance.monthly_expected_hours // 4
            if instance.monthly_expected_hours
            else 0
        )

        return {
            "this_week": project_hours.get("this_week_h") or 0,
            "last_week": project_hours.get("last_week_h") or 0,
            "weekly_expected": weekly_expected,
        }

    def _get_leave_info(self, instance):
        """Calculate all leave types in a single query"""
        leave_counts = Leave.objects.filter(
            employee=instance, end_date__year=self.current_year, status="Approved"
        ).aggregate(
            casual=Sum(
                Case(
                    When(leave_type__in=["casual"], then=1),
                    When(leave_type__in=["half_day"], then=0.5),
                    default=0,
                    output_field=FloatField(),
                )
            ),
            medical=Sum(
                Case(
                    When(leave_type__in=["medical"], then=1),
                    When(leave_type__in=["half_day_medical"], then=0.5),
                    default=0,
                    output_field=FloatField(),
                )
            ),
            non_paid=Sum(
                Case(
                    When(leave_type="non_paid", then=1),
                    default=0,
                    output_field=FloatField(),
                )
            ),
        )
        leave_mgmt = instance.leave_management
        return {
            "passed_casual": leave_counts.get("casual") or 0,
            "total_casual": leave_mgmt.casual_leave or 0,
            "passed_medical": leave_counts.get("medical") or 0,
            "total_medical": leave_mgmt.medical_leave or 0,
            "passed_non_paid": leave_counts.get("non_paid") or 0,
        }

    def _project_hour_statistic(self, instance):
        hour_data = (
            instance.employeeprojecthour_set.filter(created_at__year=self.current_year)
            .annotate(month=functions.ExtractMonth("created_at"))
            .values("month")
            .annotate(total_hours=functions.Round(Sum("hours"), precision=2))
            .order_by("month")
        )
        d = {item["month"]: item["total_hours"] for item in hour_data}
        data = [
            {"month": month_abbr[i], "total_hours": d.get(i, 0)} for i in range(1, 13)
        ]
        return data

    def _late_fine_info(self, instance):
        late_fines = instance.lateattendancefine_set.filter(
            is_consider=False
        ).aggregate(
            this_month=Sum(
                "id",
                filter=Q(
                    date__year=self.current_date.year,
                    date__month=self.current_date.month,
                ),
            ),
            last_month=Sum(
                "id",
                filter=Q(
                    date__year=self.last_month.year, date__month=self.last_month.month
                ),
            ),
        )

        total_late_day = instance.employeeattendance_set.filter(
            date__year=self.current_date.year,
            date__month=self.current_date.month,
            entry_time__gt=datetime.time(11, 10),
        ).count()

        return {
            "this_month": (late_fines.get("this_month") or 0) * 80,
            "last_month": (late_fines.get("last_month") or 0) * 80,
            "total_late_day": total_late_day,
        }

    def _get_last_week_attendance(self, instance):
        from django.utils.timezone import timedelta

        today = timezone.now().date()
        weekday = today.weekday()  # Monday=0, Sunday=6

        # Current week's Monday
        this_monday = today - timedelta(days=weekday)

        # Last week's Monday to Friday
        last_monday = this_monday - timedelta(days=7)
        last_friday = last_monday + timedelta(days=4)

        activities = (
            EmployeeActivity.objects.filter(
                employee_attendance__employee_id=instance,
                employee_attendance__date__range=[last_monday, last_friday],
                start_time__isnull=False,
                end_time__isnull=False,
            )
            .annotate(
                duration=ExpressionWrapper(
                    F("end_time") - F("start_time"), output_field=DurationField()
                )
            )
            .values("employee_attendance__id", "employee_attendance__date")
            .annotate(
                total_seconds=Sum(ExtractEpoch(F("start_time"), F("end_time"))),
                outside_hours=ExpressionWrapper(
                    F("total_seconds") / 3600 * 0.1, output_field=FloatField()
                ),
                inside_hours=ExpressionWrapper(
                    F("total_seconds") / 3600 * 0.9, output_field=FloatField()
                ),
            )
            .values("outside_hours", "inside_hours")
        )
        return activities

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["project_hours"] = self._get_project_hour(instance)
        data["leave_info"] = self._get_leave_info(instance)
        data["project_hour_statistic"] = self._project_hour_statistic(instance)
        data["late_fine_info"] = self._late_fine_info(instance)
        data["last_week_attendance"] = self._get_last_week_attendance(instance)
        return data
