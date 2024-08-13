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
    actions = ["approve_selected"]

    def has_module_permission(self, request):
        return False

    def get_fields(self, request, obj):
        form_fields = super(InvestmentAllowanceAdmin, self).get_fields(request, obj)
        field_ = list(form_fields)
        if not request.user.is_superuser and not request.user.has_perm(
            "account.tax_information_approved"
        ):
            field_.remove("approved")
        return tuple(field_)

    @admin.action
    def approve_selected(self, request, queryset):
        queryset.update(approved=True)


class VehicleRebateAttachmentInline(admin.TabularInline):
    model = VehicleRebateAttachment


@admin.register(VehicleRebate)
class VehicleRebateAdmin(admin.ModelAdmin):
    list_display = ["employee", "amount"]
    inlines = [VehicleRebateAttachmentInline]
    autocomplete_fields = ["employee"]
    search_fields = ["employee__active"]
    fields = ("employee", "amount", "approved")
    actions = ["approve_selected"]

    def get_fields(self, request, obj):
        form_fields = super(VehicleRebateAdmin, self).get_fields(request, obj)
        field_ = list(form_fields)
        if not request.user.is_superuser and not request.user.has_perm(
            "account.tax_information_approved"
        ):
            field_.remove("approved")
        return tuple(field_)

    @admin.action
    def approve_selected(self, request, queryset):
        queryset.update(approved=True)

    def has_module_permission(self, request):
        return False
