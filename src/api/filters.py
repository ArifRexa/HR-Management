from django_filters import rest_framework as filters

from project_management.models import DailyProjectUpdate


class DailyProjectUpdateFilter(filters.FilterSet):
    created_at = filters.DateRangeFilter(
        field_name="created_at", lookup_expr="date__range"
    )

    class Meta:
        model = DailyProjectUpdate
        fields = ["status", "project", "employee", "manager", "created_at"]
