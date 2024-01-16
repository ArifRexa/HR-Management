from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
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
        BlogContextInline,
        # BlogTagInline,
    )

    search_fields = ("title",)
    autocomplete_fields = ["category"]
    list_display = (
        "title",
        "slug",
        "active",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        querySet = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return querySet
        else:
            return querySet.filter(created_by=user)

    def get_form(
        self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any
    ) -> Any:
        try:
            form = super().get_form(request, obj, change, **kwargs)
            form.base_fields["active"].disabled = not request.user.has_perm(
                "website.can_approve"
            )
        except Exception:
            form = super().get_form(request, obj, **kwargs)
        return form

    def has_change_permission(self, request, obj=None):
        permitted = super().has_change_permission(request, obj=obj)
        if request.user.is_superuser:
            return True
        if permitted and obj:
            return not obj.active
        return False

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        form.base_fields["active"].disabled = not request.user.has_perm(
            "website.can_approve"
        )
        return super().save_model(request, obj, form, change)
