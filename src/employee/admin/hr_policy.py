from django.contrib import admin

from employee.models import HRPolicy, HRPolicySection, HRPolicyPublic


class HRPolicySectionAdmin(admin.TabularInline):
    model = HRPolicySection
    extra = 1


@admin.register(HRPolicy)
class HRPolicyAdmin(admin.ModelAdmin):
    list_display = ("title", "active")
    search_fields = ("title", "description")
    list_filter = ("active",)
    inlines = (HRPolicySectionAdmin,)

    def has_module_permission(self, request):
        return False


@admin.register(HRPolicyPublic)
class HRContractPolicies(admin.ModelAdmin):
    change_list_template = "admin/employee/hr_policy.html"
    search_fields = (
        "hrpolicysection__title",
        "hrpolicysection__description",
    )

    def get_queryset(self, request):
        qs = (
            super()
            .get_queryset(request)
            .filter(active=True)
            .prefetch_related("hrpolicysection_set")
        )
        return qs

    def has_module_permission(self, request):
        return False
