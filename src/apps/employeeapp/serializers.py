from rest_framework import serializers
from apps.authentication.serializers import UserSerializer
from apps.mixin.serializer import BaseModelSerializer
from employee.models.employee import Employee


class EmployeeSerializer(BaseModelSerializer):
    user = UserSerializer(read_only=True)
    permissions = serializers.SerializerMethodField()
    
    def get_permissions(self, obj):
        return obj.user.get_all_permissions()

    class Meta:
        model = Employee
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True},
        }
        ref_name = "api_employee"
