from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest

# Register your models here.
from website.models import (
    Service,
    Blog,
    Category,
    Tag,
    BlogCategory,
    BlogTag,
    BlogContext,
)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order", "active")
    search_fields = ("title",)

    def has_module_permission(self, request):
        return False


@admin.register(Category)
class Category(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def has_module_permission(self, request):
        return False


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def has_module_permission(self, request):
        return False


class BlogCategoryInline(admin.StackedInline):
    model = BlogCategory
    extra = 1
    autocomplete_fields = ("category",)


class BlogTagInline(admin.StackedInline):
    model = BlogTag
    extra = 1
    autocomplete_fields = ("tag",)


class BlogContextInline(admin.TabularInline):
    model = BlogContext
    extra = 1


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

    inlines = (
        BlogCategoryInline,
        BlogContextInline,
        # BlogTagInline,
    )

    # readonly_fields = ("read_time_minute",)
    search_fields = ("title",)
    list_display = (
        "title",
        "slug",
        "active",
    )

    def get_form(
        self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any
    ) -> Any:
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["active"].disabled = not request.user.has_perm(
            "website.can_approve"
        )
        return form

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        form.base_fields["active"].disabled = not request.user.has_perm(
            "website.can_approve"
        )
        return super().save_model(request, obj, form, change)
