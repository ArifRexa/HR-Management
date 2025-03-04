from django_filters import rest_framework as filters


class BaseFilterSet(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()
    
    
