from apps.mixin.views import BaseModelViewSet
from employee.models.employee import Employee
from rest_framework import views
from rest_framework.response import Response
from .serializers import DashboardSerializer, EmployeeSerializer


class EmployeeViewSet(BaseModelViewSet):
    queryset = (
        Employee.objects.select_related("user", "user__profile", "user__userlogs")
        .prefetch_related(
            "leave_set",
            "dailyprojectupdate_employee",
            "dailyprojectupdate_manager",
        )
        .order_by("id")
    )
    serializer_class = EmployeeSerializer


class DashboardView(views.APIView):
    def get(self, request, *args, **kwargs):
        employee = Employee.objects.get(user=request.user)
        serializer = DashboardSerializer(employee)
        return Response(serializer.data)