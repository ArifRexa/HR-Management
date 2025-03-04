from apps.mixin.filters import BaseFilterSet
from project_management.models import DailyProjectUpdate, ProjectHour


class DailyProjectUpdateFilter(BaseFilterSet):

    class Meta:
        model = DailyProjectUpdate
        fields = ["status", "project", "employee", "manager", "created_at"]


class ProjectHourFilter(BaseFilterSet):

    class Meta:
        model = ProjectHour
        fields = ["project", "manager", "tpm", "status", "hour_type", "created_at"]
