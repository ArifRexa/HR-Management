from rest_framework import permissions

from apps.mixin.views import BaseModelViewSet
from employee.models.employee import Employee

from .serializers import EmployeeSerializer


class EmployeeViewSet(BaseModelViewSet):
    queryset = Employee.objects.select_related(
        "user", "user__profile", "user__userlogs"
    ).prefetch_related(
        "leave_set",
        "dailyprojectupdate_employee",
        "dailyprojectupdate_manager",
    )
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
