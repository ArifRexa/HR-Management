from django.contrib import admin
from django.contrib.auth.models import User

from account.models import Fund, FundCategory
from config.admin import RecentEdit

@admin.register(FundCategory)
class FundCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')
    search_fields = ['title']

    def has_module_permission(self, request):
        return False

@admin.register(Fund)
class FundAdmin(RecentEdit, admin.ModelAdmin):
    list_display = ['date', 'amount', 'user', 'fund_category', 'note']
    list_filter = ['date', 'user']
    autocomplete_fields = ['user', 'fund_category']
    