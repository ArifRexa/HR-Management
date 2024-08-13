from django.contrib import admin


from account.models import (
    InvestmentAllowance,
    InvestmentAllowanceAttachment,
    VehicleRebate,
    VehicleRebateAttachment,
)


class InvestmentAllowanceAttachmentInline(admin.TabularInline):
    model = InvestmentAllowanceAttachment


@admin.register(InvestmentAllowance)
class InvestmentAllowanceAdmin(admin.ModelAdmin):
    list_display = ["employee", "amount"]
    inlines = [InvestmentAllowanceAttachmentInline]
    autocomplete_fields = ["employee"]

    def has_module_permission(self, request):
        return False


class VehicleRebateAttachmentInline(admin.TabularInline):
    model = VehicleRebateAttachment


@admin.register(VehicleRebate)
class VehicleRebateAdmin(admin.ModelAdmin):
    list_display = ["employee", "amount"]
    inlines = [VehicleRebateAttachmentInline]
    autocomplete_fields = ["employee"]
    search_fields = ["employee__active"]


    def has_module_permission(self, request):
        return False
