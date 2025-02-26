from rest_framework import viewsets, permissions, parsers, decorators, status
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import DailyProjectUpdateFilter
from api.serializer import (
    BulkDailyUpdateSerializer,
    DailyProjectUpdateCreateSerializer,
    StatusUpdateSerializer,
)
from project_management.models import DailyProjectUpdate
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import FileResponse
from io import BytesIO


from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework.pagination import LimitOffsetPagination, CursorPagination

class FasterDjangoPaginator(Paginator):
    @cached_property
    def count(self):
        # only select 'id' for counting, much cheaper
        return self.object_list.values('id').count()


class FasterPageNumberPagination(CursorPagination):
    ordering = "-created_by"


class DailyProjectUpdateViewSet(viewsets.ModelViewSet):
    queryset = (
        DailyProjectUpdate.objects.select_related(
            "employee", "manager", "project"
        )
        .prefetch_related("history", "dailyprojectupdateattachment_set", "employee__leave_set", "project__client")
        .all()
    )
    serializer_class = DailyProjectUpdateCreateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DailyProjectUpdateFilter
    search_fields = (
        "employee__full_name",
        "project__title",
        "manager__full_name",
    )
    permission_classes = [permissions.IsAuthenticated]
    # pagination_class = FasterPageNumberPagination

    def get_serializer_class(self):
        if self.action == "status_update":
            return StatusUpdateSerializer
        if self.action == "export_update":
            return BulkDailyUpdateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        self.parser_classes = [
            parsers.MultiPartParser,
            parsers.FormParser,
        ]
        return super().create(request, *args, **kwargs)

    @decorators.action(detail=False, methods=["PATCH"], url_path="status-update")
    def status_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        queryset = self.filter_queryset(
            self.get_queryset()
            .filter(id__in=data["update_ids"])
            .select_related("employee", "project").prefetch_related("history", "dailyprojectupdateattachment_set")
        )
        updates = list(queryset)
        for update in updates:
            update.status = data["status"]
        DailyProjectUpdate.objects.bulk_update(updates, ["status"])
        return Response(DailyProjectUpdateCreateSerializer(queryset, many=True).data)

    @decorators.action(detail=False, methods=["POST"], url_path="export-updates")
    def export_update(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use values() to optimize query
        queryset = (
            self.get_queryset()
            .filter(id__in=serializer.validated_data.get("update_ids", []))
            .select_related("employee", "project")
            .values(
                "employee__full_name", "updates_json", "created_at", "project__title"
            )
        )
        queryset = self.filter_queryset(queryset)

        if not queryset:
            return Response(
                {"error": "No records found for export."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use annotate for calculations
        total_hours = queryset.aggregate(total=Sum("hours"))["total"] or 0

        # Group updates by employee
        updates_by_employee = {}
        for update in queryset:
            if not update["updates_json"]:
                continue

            emp_name = update["employee__full_name"]
            if emp_name not in updates_by_employee:
                updates_by_employee[emp_name] = []

            updates_by_employee[emp_name].extend(update["updates_json"])

        # Build file content more efficiently
        content = [
            "Today's Update\n",
            "-----------------\n",
            f"{queryset[0]['created_at'].strftime('%d-%m-%Y')}\n\n",
            f"Total Hours: {round(total_hours, 3)}H\n\n",
        ]

        for emp_name, updates in updates_by_employee.items():
            content.extend(
                [
                    f"{emp_name}\n\n",
                    "\n".join(f"{u[0]} - {u[1]}H." for u in updates),
                    "\n\nAssociated Links:\n",
                    "\n".join(f"{i+1}. {u[2]}" for i, u in enumerate(updates)),
                    "\n-------------------------------------------------------------\n\n",
                ]
            )

        response = FileResponse(
            BytesIO("".join(content).encode("utf-8")), content_type="text/plain"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{queryset[0]["project__title"].replace(" ", "_")}_'
            f'{queryset[0]["created_at"].strftime("%d-%m-%Y")}.txt"'
        )
        return response
