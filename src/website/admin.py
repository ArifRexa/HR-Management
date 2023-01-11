from django.contrib import admin

# Register your models here.
from website.models import Service, Blog, Category, Tag, BlogCategory, BlogTag


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order', 'active')
    search_fields = ('title',)


@admin.register(Category)
class Category(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class BlogCategoryInline(admin.StackedInline):
    model = BlogCategory
    extra = 1
    autocomplete_fields = ('category',)


class BlogTagInline(admin.StackedInline):
    model = BlogTag
    extra = 1
    autocomplete_fields = ('tag',)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = (
        BlogCategoryInline, 
        # BlogTagInline,
    )
    readonly_fields = ('read_time_minute', )
    search_fields = ('title', )
    list_display = ('title', 'slug', 'active', )
