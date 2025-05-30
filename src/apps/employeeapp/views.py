from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, views, parsers
from rest_framework.response import Response

from apps.employeeapp.filters import EmployeeFilter
from apps.mixin.views import BaseModelViewSet
from employee.models.employee import Employee
from employee.models.employee_skill import EmployeeSkill
from django.db.models import Prefetch
from .serializers import DashboardSerializer, EmployeeSerializer


class EmployeeViewSet(BaseModelViewSet):
    queryset = (
        Employee.objects.select_related("user", "user__profile", "user__userlogs", "designation")
        .prefetch_related(
            "leave_set",
            "dailyprojectupdate_employee",
            "dailyprojectupdate_manager",
            Prefetch("employeeskill_set", queryset=EmployeeSkill.objects.select_related("skill").all()),
        )
        .order_by("id")
    )
    filterset_class = EmployeeFilter
    serializer_class = EmployeeSerializer
    search_fields = ["full_name", "user__email", "email"]
    
    

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "is_active",
                openapi.IN_QUERY,
                description="employee is active or not",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "is_permanent",
                openapi.IN_QUERY,
                description="employee is permanent or not",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "is_lead",
                openapi.IN_QUERY,
                description="employee is lead or not",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "is_manager",
                openapi.IN_QUERY,
                description="employee is manager or not",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "created_at_after",
                openapi.IN_QUERY,
                description="created_at from date",
                type=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "created_at_before",
                openapi.IN_QUERY,
                description="created_at to date",
                type=openapi.FORMAT_DATE,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class EmployeeDashboardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        employee = Employee.objects.get(user=request.user)
        serializer = DashboardSerializer(employee)
        return Response(serializer.data)
