from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce

from account.models import Expense

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = ('username', 'first_name', 'last_name')
    list_display = ('username', 'full_name', 'email', 'get_fund', 'is_staff', 'is_active')
    
    class Media:
        js = ("js/custom_permission_search.js",)

    @admin.display()
    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    @admin.display(description='Current Fund')
    def get_fund(self, obj):
        fund_added = obj.fund_set.aggregate(total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
        fund_subtract = Expense.objects.filter(approved_by=obj).aggregate(
            total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
        return fund_added - fund_subtract
