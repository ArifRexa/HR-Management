from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from .filters import BaseFilterSet
from .swagger_schema import CustomSwaggerAutoSchema


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
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
        ],
        auto_schema=CustomSwaggerAutoSchema,
    ),
)
class BaseModelViewSet(viewsets.ModelViewSet):
    serializers = {}
    querysets = {}
    permissions = {}
    filter_backends = [DjangoFilterBackend]
    filterset_class = BaseFilterSet
    http_method_names = ["get", "post", "put", "patch", "delete"]
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        return self.serializers.get(self.action, super().get_serializer_class())

    def get_queryset(self):
        return self.querysets.get(self.action, super().get_queryset())

    def get_permissions(self):
        return self.permissions.get(self.action, super().get_permissions())

    class Meta:
        abstract = True
