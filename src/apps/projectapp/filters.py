from django_filters import rest_framework as filters

from apps.mixin.filters import BaseFilterSet
from project_management.models import DailyProjectUpdate, ProjectHour


class DailyProjectUpdateFilter(BaseFilterSet):

    class Meta:
        model = DailyProjectUpdate
        fields = ["status", "project", "employee", "manager", "created_at"]


class ProjectHourFilter(BaseFilterSet):
    payment_method = filters.CharFilter(
        field_name="project__client__payment_method", lookup_expr="icontains"
    )
    invoice_type = filters.CharFilter(
        field_name="project__client__invoice_type", lookup_expr="icontains"
    )
    client = filters.CharFilter(field_name="project__client", lookup_expr="exact")

    class Meta:
        model = ProjectHour
        fields = [
            "project",
            "manager",
            "tpm",
            "status",
            "hour_type",
            "created_at",
            "payment_method",
            "invoice_type",
            "client",
        ]
