from django.contrib import admin
from django.contrib.auth.models import User

from account.models import Fund
from config.admin import RecentEdit


@admin.register(Fund)
class FundAdmin(RecentEdit, admin.ModelAdmin):
    list_display = ['date', 'amount', 'user', 'note']
    list_filter = ['date', 'user']
    autocomplete_fields = ['user']
