from urllib.parse import urlparse

from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html


from asset_management.models import (
    Asset,
    # AssetCategory,
    EmployeeAssignedAsset,
    EmployeeAsset,
    AssetHead,
    Addition,
    AssetItem,
)


# @admin.register(AssetCategory)
# class AssetCategoryAdmin(admin.ModelAdmin):
#     def has_module_permission(self, request):
#         return False


@admin.register(AssetHead)
class AssetHeadAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_module_permission(self, request):
        return False


@admin.register(AssetItem)
class AssetItemAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_module_permission(self, request):
        return False


@admin.register(Addition)
class AdditionAdmin(admin.ModelAdmin):
    list_display = ("title",)
    
    def has_module_permission(self, request):
        return False


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "code",
        # "category",
        "description",
        "is_active",
        "is_available",
    )
    search_fields = (
        "title",
        "code",
        "description",
    )
    fields = (
        "title",
        "code",
        "description",
        "date",
        "rate",
        "addition",
        "head",
        "item",
        "is_available",
        "is_active",
    )
    # exclude = ("head",)
    list_filter = (
        "head",
        "is_active",
        "is_available",
    )
    change_form_template = "admin/asset/asset_change_form.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}

        if object_id:
            extra_context["assign_history"] = EmployeeAssignedAsset.objects.filter(
                asset_id=object_id
            ).order_by("-id")

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        data = request.GET.dict()

        app_label = data.get("app_label")
        model_name = data.get("model_name")
        referer = request.META.get("HTTP_REFERER", "")

        if (
            request.user.is_authenticated
            and app_label == "asset_management"
            and model_name == "employeeassignedasset"
        ):
            if "asset_management/employeeasset" in referer:
                url_parts = urlparse(referer).path.split("/")
                if len(url_parts) >= 3:
                    employee_id = url_parts[-3]
                    assined_assets = list(
                        EmployeeAssignedAsset.objects.filter(
                            employee_id=employee_id
                        ).values_list("asset_id", flat=True)
                    )
                    qs = Asset.objects.filter(
                        Q(title__icontains=search_term)
                        | Q(code__icontains=search_term)
                        | Q(is_available=True)
                        | Q(id__in=assined_assets),
                    )
        return qs, use_distinct


# @admin.register(EmployeeAssignedAsset)
# class EmployeeAssignedAssetAdmin(admin.ModelAdmin):
#     list_display = ('employee', 'asset', 'get_asset_category', )
#     autocomplete_fields = ('asset', )
#     list_filter = (
#         'asset__category',
#         ('employee', admin.RelatedOnlyFieldListFilter),
#     )
#     search_fields = (
#         'employee__full_name',
#         'asset__title',
#         'asset__category__title',
#         'asset__code',
#     )

#     @admin.display(description="Category")
#     def get_asset_category(self, obj):
#         return obj.asset.category.title


class EmployeeAssignedAssetAdmin(admin.StackedInline):
    model = EmployeeAssignedAsset
    extra = 0
    autocomplete_fields = ("asset",)
    exclude = ("end_date",)

    def get_formset(self, request, obj=None, **kwargs):
        # Pass the parent instance (obj) to the formset
        self.parent_instance = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "asset":
            # Use self.parent_instance to access the parent object
            if self.parent_instance:
                # Get the employee related to the parent instance
                employee = self.parent_instance
                # Find the last assigned asset for this employee
                last_assigned_asset = (
                    EmployeeAssignedAsset.objects.filter(employee=employee)
                    .order_by("-id")
                    .first()
                )
                # Determine if the last assigned asset is the current asset
                if last_assigned_asset:
                    last_asset_id = last_assigned_asset.asset_id
                else:
                    last_asset_id = None

                # Filter to include available assets or the last assigned asset
                kwargs["queryset"] = Asset.objects.filter(
                    Q(is_available=True) | Q(id=last_asset_id)
                )
            else:
                # If no parent instance, show only available assets
                kwargs["queryset"] = Asset.objects.filter(is_available=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class EmployeeAssetCategoryFilter(admin.SimpleListFilter):
#     title = "Asset Category"
#     parameter_name = "employeeassignedasset__asset__category_id"

#     def lookups(self, request, model_admin):
#         objs = AssetCategory.objects.all()
#         lookups = [
#             (
#                 ac.id,
#                 ac.title,
#             )
#             for ac in objs
#         ]
#         return tuple(lookups)

#     def queryset(self, request, queryset):
#         value = self.value()
#         if value is not None:
#             return queryset.filter(employeeassignedasset__asset__category_id=value)
#         return queryset


@admin.register(EmployeeAsset)
class EmployeeAssetAdmin(admin.ModelAdmin):
    fields = (
        "full_name",
        "email",
    )
    readonly_fields = (
        "full_name",
        "email",
    )

    inlines = (EmployeeAssignedAssetAdmin,)

    list_display = (
        "full_name",
        "get_assets",
    )
    list_filter = (
        "full_name",
        # EmployeeAssetCategoryFilter,
    )

    @admin.display(description="Assigned Assets")
    def get_assets(self, obj):
        # print(dir(obj))
        assigned_assets = obj.assigned_assets.all()
        assets_str = "<br>".join(
            [
                f"{assignedasset.asset.title} | {assignedasset.asset.code}"
                for assignedasset in assigned_assets
            ]
        )
        return format_html(assets_str)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(active=True)
        return qs
