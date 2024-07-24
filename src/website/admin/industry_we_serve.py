from django.http import HttpRequest
from website.model_v2.industry_we_serve import (
    IndustryPage,
    IndustryWeServeContent,
    IndustryWeServe,
)
from django.contrib import admin


class IndustryWeServeInline(admin.TabularInline):
    model = IndustryWeServe
    extra = 1


@admin.register(IndustryPage)
class IndustryPageAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (IndustryWeServeInline,)


class IndustryWeServeContentInline(admin.StackedInline):
    model = IndustryWeServeContent
    extra = 1
    prepopulated_fields = {"slug": ("title",)}
    fields = [
        "title",
        "slug",
        "description",
        "content",
        "image",
        "is_active",
    ]


@admin.register(IndustryWeServe)
class IndustryWeServeAdmin(admin.ModelAdmin):
    list_display = ("title", "page", "is_active")
    inlines = (IndustryWeServeContentInline,)
    prepopulated_fields = {"slug": ("title",)}
    fields = [
        "page",
        "title",
        "slug",
        "description",
        "image",
        "is_active",
    ]


@admin.register(IndustryWeServeContent)
class IndustryWeServeContentAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    fields = [
        "industry",
        "title",
        "slug",
        "description",
        "content",
        "image",
        "is_active",
    ]
