from rest_framework import serializers

from employee.models import Employee
from project_management.models import Project
from website.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
