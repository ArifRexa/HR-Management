from django.contrib import admin

from account.models import InvestmentAllowance, InvestmentAllowanceAttachment


class InvestmentAllowanceAttachmentInline(admin.TabularInline):
    model = InvestmentAllowanceAttachment

@admin.register(InvestmentAllowance)
class InvestmentAllowanceAdmin(admin.ModelAdmin):
    list_display = ["employee", "amount"]
    inlines = [InvestmentAllowanceAttachmentInline]
    autocomplete_fields = ["employee"]
    def has_module_permission(self, request):
        return False