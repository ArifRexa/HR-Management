from collections.abc import Sequence

from django.db.models.query import QuerySet
from django.contrib import admin
from django.http import HttpRequest

from provident_fund.models import MonthlyEntry


@admin.register(MonthlyEntry)
class ProvidentFundMonthlyEntryAdmin(admin.ModelAdmin):
    list_display = (
        'get_employee',
        'tranx_date',
        'amount',
        'basic_salary',
    )
    list_filter = (
        'account__employee',
    )
    search_fields = (
        'account__employee__full_name',
    )
    autocomplete_fields = (
        'account',
    )
    fieldsets = (
        (None, {
            'fields': ('account', 'tranx_date', 'amount', 'basic_salary',),
        }),
        # ('More', {
        #     'fields': ('note', 'end_date', 'active'),
        # }),
    )
    
    date_hierarchy = 'tranx_date'
    list_per_page = 20

    @admin.display(description="Employee", ordering="account__employee__full_name")
    def get_employee(self, obj:MonthlyEntry):
        return obj.account.__str__()

    def get_queryset(self, request: HttpRequest) -> QuerySet[MonthlyEntry]:
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(account=request.user.employee.pf_account)
        return qs
    
    def get_list_filter(self, request: HttpRequest) -> Sequence[str]:
        list_filter = super().get_list_filter(request)
        if not request.user.is_superuser:
            list_filter = []

        return list_filter

