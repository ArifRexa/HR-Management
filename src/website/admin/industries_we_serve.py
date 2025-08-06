from django.contrib import admin
import nested_admin

from website.models import IndustryKeyword, IndustryMetadata
from website.models_v2.industries_we_serve import ApplicationAreas, IndustryServe, ServeCategory

class ApplicationAreasInline(nested_admin.NestedStackedInline):
    model = ApplicationAreas
    extra = 0

class IndustryKeywordInline(nested_admin.NestedStackedInline):
    model = IndustryKeyword
    extra = 1
class IndustryMetadataInline(nested_admin.NestedStackedInline):
    model = IndustryMetadata
    extra = 1
    inlines = [IndustryKeywordInline]

# @admin.register(ServeCategory)
# class ServeCategoryAdmin(nested_admin.NestedModelAdmin):
#     list_display = ('title', 'slug',)
#     inlines = [ApplicationAreasInline,IndustryMetadataInline]
#     prepopulated_fields = {'slug': ('title',)}

class ServeCategoryInline(admin.TabularInline):
    model = IndustryServe.serve_categories.through
    extra = 1

@admin.register(IndustryServe)
class IndustryServeAdmin(admin.ModelAdmin):
    inlines = [ServeCategoryInline]
    list_display = ('title',)
    search_fields = ('title',)
    exclude = ('serve_categories',)
    # filter_horizontal = ('serve_categories',)
