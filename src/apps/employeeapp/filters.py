from django_filters import FilterSet
from django.db.models import Q

from employee.models.employee import Employee


class EmployeeFilter(FilterSet):
    class Meta:
        model = Employee
        fields = []

    def filter_queryset(self, queryset):
        lead = self.data.get("is_lead") in ["true", "1"]
        manager = self.data.get("is_manager") in ["true", "1"]

        if lead and manager:
            return queryset.filter(Q(lead=True) | Q(manager=True))
        elif lead:
            return queryset.filter(lead=True)
        elif manager:
            return queryset.filter(manager=True)
        return queryset
