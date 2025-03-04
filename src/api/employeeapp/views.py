from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework import viewsets, permissions
from .serializers import EmployeeSerializer

from employee.models.employee import Employee


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related(
        "user", "user__profile", "user__userlogs"
    ).prefetch_related(
        "leave_set",
        "dailyprojectupdate_employee",
        "dailyprojectupdate_manager",
    )
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
