from django_filters import FilterSet, rest_framework as dj_filters
from django.db.models import Q

from employee.models.employee import Employee


class EmployeeFilter(FilterSet):
    is_active = dj_filters.BooleanFilter(field_name="active")
    is_lead = dj_filters.BooleanFilter(field_name="lead")
    is_manager = dj_filters.BooleanFilter(field_name="manager")
    is_permanent = dj_filters.BooleanFilter(method="filter_is_permanent")
    
    def filter_is_permanent(self, queryset, name, value):
        if value is None:
            return queryset
        elif not bool(value):
            return queryset.filter(Q(permanent_date__isnull=True))
        return queryset.filter(Q(permanent_date__isnull=False))
    
    class Meta:
        model = Employee
        fields = ["is_active", "is_lead", "is_manager", "is_permanent"]

    # def filter_queryset(self, queryset):
    #     lead = self.data.get("is_lead") in ["true", "1"]
    #     manager = self.data.get("is_manager") in ["true", "1"]

    #     if lead and manager:
    #         return queryset.filter(Q(lead=True) | Q(manager=True))
    #     elif lead:
    #         return queryset.filter(lead=True)
    #     elif manager:
    #         return queryset.filter(manager=True)
    #     return queryset
