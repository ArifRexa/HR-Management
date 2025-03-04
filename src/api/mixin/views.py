from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BaseFilterSet


class BaseModelViewSet(viewsets.ModelViewSet):
    serializers = {}
    querysets = {}
    permissions = {}
    filter_backends = [DjangoFilterBackend]
    filterset_class = BaseFilterSet
