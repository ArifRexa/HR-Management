from typing import Any, Union
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from mptt.admin import MPTTModelAdmin

# Register your models here.
from website.models import (
    Service,
    Blog,
    Category,
    Tag,
    BlogCategory,
    BlogTag,
    BlogContext,
    BlogComment,
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

    inlines = (BlogContextInline,)

    search_fields = ("title",)
    autocomplete_fields = ["category", "tag"]
    list_display = (
        "title",
        "author",
        "slug",
        "created_at",
        "updated_at",
        "active",
    )

    @admin.display(description="Created By")
    def author(self, obj):
        author = obj.created_by
        return f"{author.first_name} {author.last_name}"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        querySet = super().get_queryset(request)
        user = request.user
        if user.has_perm("website.can_view_all"):
            return querySet
        else:
            return querySet.filter(created_by=user)

    def get_form(
        self, request: Any, obj: Union[Any, None] = ..., change: bool = ..., **kwargs: Any
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
        if permitted and request.user.has_perm("website.can_change_after_approve"):
            return True
        if permitted and obj:
            return not obj.active and obj.created_by == request.user
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Union[Any, None] = ...
    ) -> bool:
        permitted = super().has_delete_permission(request, obj)
        user = request.user
        if permitted and user.has_perm("website.can_delete_after_approve"):
            return True
        elif permitted and isinstance(obj, Blog):
            return not obj.active and obj.created_by == user
        return permitted

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        form.base_fields["active"].disabled = not request.user.has_perm(
            "website.can_approve"
        )
        return super().save_model(request, obj, form, change)


@admin.register(BlogComment)
class BlogCommentModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ["id", "name"]
