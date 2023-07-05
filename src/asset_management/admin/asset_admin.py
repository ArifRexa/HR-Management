from django.contrib import admin

from asset_management.models import Asset, AssetCategory, EmployeeAssignedAsset


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'category', 'description', 'is_active', 'is_available', )
    search_fields = ('title', 'code', 'description', )
    list_filter = (
        'category',
    )


@admin.register(EmployeeAssignedAsset)
class EmployeeAssignedAssetAdmin(admin.ModelAdmin):
    list_display = ('employee', 'asset', 'get_asset_category', )
    autocomplete_fields = ('asset', )
    list_filter = (
        'asset__category', 
        ('employee', admin.RelatedOnlyFieldListFilter),
    )

    @admin.display(description="Category")
    def get_asset_category(self, obj):
        return obj.asset.category.title

