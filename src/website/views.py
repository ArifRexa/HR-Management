from django.http import Http404
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from employee.models import Employee
from project_management.models import Project
from website.models import Service
from website.serializers import ServiceSerializer, ProjectSerializer, EmployeeSerializer, ServiceDetailsSerializer, \
    ProjectDetailsSerializer, EmployeeDetailsSerializer


def index(request):
    return render(request, 'webdoc/index.html')


class ServiceList(APIView):
    def get(self, request, format=None):
        services = Service.objects.filter(active=True).order_by('order').all()
        serializer = ServiceSerializer(services, many=True, context={'request': request})
        return Response(serializer.data)


class ServiceDetails(APIView):

    def get_object(self, slug):
        try:
            return Service.objects.filter(active=True).get(slug__exact=slug)
        except Service.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        service = self.get_object(slug)
        serializer = ServiceDetailsSerializer(service, context={'request': request})
        return Response(serializer.data)


class ProjectList(APIView):
    def get(self, request, format=None):
        projects = Project.objects.filter(show_in_website=True).all()
        serializer = ProjectSerializer(projects, many=True, context={'request': request})
        return Response(serializer.data)


class ProjectDetails(APIView):
    def get_object(self, slug):
        try:
            return Project.objects.filter(show_in_website=True).get(slug__exact=slug)
        except Service.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        projects = self.get_object(slug)
        serializer = ProjectDetailsSerializer(projects, context={'request': request})
        return Response(serializer.data)


class EmployeeList(APIView):
    def get(self, request, format=None):
        employees = Employee.objects.filter(active=True, show_in_web=True).order_by('joining_date', '-manager', 'list_order', ).all()
        serializer = EmployeeSerializer(employees, many=True, context={'request': request})
        return Response(serializer.data)


class EmployeeDetails(APIView):
    def get_object(self, slug):
        try:
            return Employee.objects.get(slug__exact=slug)
        except Employee.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        employee = self.get_object(slug)
        serializer = EmployeeDetailsSerializer(employee, context={'request': request})
        return Response(serializer.data)
