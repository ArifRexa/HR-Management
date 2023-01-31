from django.db.models.query import QuerySet
from django.contrib import admin
from django.http import HttpRequest

from provident_fund.models import Account


@admin.register(Account)
class ProvidentFundAccountAdmin(admin.ModelAdmin):
    list_display = (
        'get_employee',
        'start_date',
        'active',
    )
    list_filter = (
        'active',
    )
    search_fields = (
        'employee__full_name',
    )
    autocomplete_fields = (
        'employee',
    )
    fieldsets = (
        (None, {
            'fields': ('employee', 'start_date', 'maturity_date', 'scale',),
        }),
        ('More', {
            'fields': ('note', 'end_date', 'active'),
        }),
    )
    ordering = (
        '-active',
    )
    
    date_hierarchy = 'start_date'
    list_per_page = 20

    def get_queryset(self, request: HttpRequest) -> QuerySet[Account]:
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(employee=request.user.employee)
        return qs
    
    @admin.display(description="Employee", ordering="employee__full_name")
    def get_employee(self, obj:Account):
        return obj.__str__()

