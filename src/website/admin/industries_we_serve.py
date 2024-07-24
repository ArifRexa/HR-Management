from django.contrib import admin

from website.models_v2.industries_we_serve import ApplicationAreas, ServeCategory

class ApplicationAreasInline(admin.TabularInline):
    model = ApplicationAreas
    extra = 1

@admin.register(ServeCategory)
class ServeCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'short_description', 'impressive_title')
    inlines = [ApplicationAreasInline]
    prepopulated_fields = {'slug': ('title',)}


class TitleAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_description', 'motivation_title')
    autocomplete_fields = ['serve_category']
    search_fields = ['title']
