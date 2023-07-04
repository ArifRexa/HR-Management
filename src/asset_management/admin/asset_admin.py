from django.contrib import admin

from asset_management.models import Asset, AssetCategory, EmployeeAssignedAsset


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'description', 'is_active', 'is_available', )


@admin.register(EmployeeAssignedAsset)
class EmployeeAssignedAssetAdmin(admin.ModelAdmin):
    list_display = ('employee', 'asset')

    list_filter = (
        'asset__category', 
        ('employee', admin.RelatedOnlyFieldListFilter),
    )

