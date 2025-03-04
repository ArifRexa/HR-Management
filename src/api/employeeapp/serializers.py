from api.authentication.serializers import UserSerializer
from employee.models.employee import Employee
from rest_framework import serializers

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True},
        }
        ref_name = "api_employee"

