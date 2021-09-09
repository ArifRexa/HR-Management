from django.contrib import admin

from account.models import ProfitShare


@admin.register(ProfitShare)
class ProfitShareAdmin(admin.ModelAdmin):
    list_display = ('date', 'payment_amount', 'user')
