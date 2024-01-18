import django_filters
from django.http import Http404
from django.shortcuts import render
from django.db.models import Count, Q

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters

from employee.models import Employee, EmployeeNOC
from project_management.models import Project
from website.models import Service, Category, Tag, Blog
from website.serializers import (
    ServiceSerializer,
    ProjectSerializer,
    EmployeeSerializer,
    ServiceDetailsSerializer,
    ProjectDetailsSerializer,
    EmployeeDetailsSerializer,
    CategoryListSerializer,
    TagListSerializer,
    BlogListSerializer,
    BlogDetailsSerializer,
    EmployeeNOCSerializer,
)


def index(request):
    return render(request, "webdoc/index.html")


class ServiceList(APIView):
    def get(self, request, format=None):
        services = Service.objects.filter(active=True).order_by("order").all()
        serializer = ServiceSerializer(
            services, many=True, context={"request": request}
        )
        return Response(serializer.data)


class ServiceDetails(APIView):
    def get_object(self, slug):
        try:
            return Service.objects.filter(active=True).get(slug__exact=slug)
        except Service.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        service = self.get_object(slug)
        serializer = ServiceDetailsSerializer(service, context={"request": request})
        return Response(serializer.data)


class ProjectList(APIView):
    def get(self, request, format=None):
        projects = Project.objects.filter(show_in_website=True).all()
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request}
        )
        return Response(serializer.data)


class ProjectDetails(APIView):
    def get_object(self, slug):
        try:
            return Project.objects.filter(show_in_website=True).get(slug__exact=slug)
        except Service.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        projects = self.get_object(slug)
        serializer = ProjectDetailsSerializer(projects, context={"request": request})
        return Response(serializer.data)


class EmployeeList(APIView):
    def get(self, request, format=None):
        employees = (
            Employee.objects.filter(active=True, show_in_web=True)
            .order_by(
                "joining_date",
                "-manager",
                "list_order",
            )
            .all()
        )
        serializer = EmployeeSerializer(
            employees, many=True, context={"request": request}
        )
        return Response(serializer.data)


class EmployeeDetails(APIView):
    def get_object(self, slug):
        try:
            return Employee.objects.get(slug__exact=slug)
        except Employee.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        employee = self.get_object(slug)
        serializer = EmployeeDetailsSerializer(employee, context={"request": request})
        return Response(serializer.data)


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class TagListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer


class CategoryListViewWithBlogCount(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Category.objects.annotate(
            total_blog=Count("categories", filter=Q(categories__active=True))
        ).values("id", "name", "slug", "total_blog")
        return Response(data=queryset)


class BlogListView(ListAPIView):
    queryset = Blog.objects.filter(active=True).all().order_by("-created_at")
    serializer_class = BlogListSerializer
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_fields = ["category"]
    search_fields = ["title", "category__name", "tag__name"]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response


class BlogDetailsView(RetrieveAPIView):
    lookup_field = "slug"
    queryset = Blog.objects.filter(active=True).all()
    serializer_class = BlogDetailsSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response


class VerifyDocuments(APIView):
    def get_noc(self, uuid):
        try:
            return EmployeeNOC.objects.get(uuid__exact=uuid)
        except EmployeeNOC.DoesNotExist:
            raise Http404

    def get(self, request, document_type, uuid, format=None):
        if document_type == "NOC":
            enoc = self.get_noc(uuid)
            serializer = EmployeeNOCSerializer(enoc, context={"request": request})
            return Response(serializer.data)

        raise Http404
