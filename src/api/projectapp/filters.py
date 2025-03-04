from django_filters import rest_framework as filters

from project_management.models import DailyProjectUpdate, ProjectHour


class DailyProjectUpdateFilter(filters.FilterSet):
    created_at = filters.DateRangeFilter(
        field_name="created_at", lookup_expr="date__range"
    )

    class Meta:
        model = DailyProjectUpdate
        fields = ["status", "project", "employee", "manager", "created_at"]


class ProjectHourFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = ProjectHour
        fields = ["project", "manager", "tpm", "status", "hour_type", "created_at"]
