from django.contrib import admin

from asset_management.models import Asset, AssetCategory


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
