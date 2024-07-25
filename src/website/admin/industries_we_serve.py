from django.contrib import admin

from website.models_v2.industries_we_serve import ApplicationAreas, IndustryServe, ServeCategory

class ApplicationAreasInline(admin.TabularInline):
    model = ApplicationAreas
    extra = 0

@admin.register(ServeCategory)
class ServeCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'short_description', 'impressive_title')
    inlines = [ApplicationAreasInline]
    prepopulated_fields = {'slug': ('title',)}

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
