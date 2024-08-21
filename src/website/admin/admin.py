from typing import Any, Union
from django import forms
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils import timezone
from mptt.admin import MPTTModelAdmin
from django.utils.html import format_html
from django.db import transaction
from django.forms.models import model_to_dict
import requests
from django_q.tasks import async_task

# Register your models here.
from website.models import (
    Award,
    BlogFAQ,
    BlogModeratorFeedback,
    Gallery,
    IndustryWeServe,
    LifeAtMediusware,
    Service,
    Blog,
    Category,
    Tag,
    BlogCategory,
    BlogTag,
    BlogContext,
    BlogComment,
    FAQ,
    ServiceTechnology,
    ServiceProcess,
    OurAchievement,
    OurGrowth,
    OurJourney,
    EmployeePerspective,
    Industry,
    Lead,
    ServiceContent,
    VideoTestimonial,
)
from django.forms.models import BaseInlineFormSet


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ["title", "image", "short_description"]

    def has_module_permission(self, request):
        return False


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ["image"]


class ServiceTechnologyInline(admin.TabularInline):
    model = ServiceTechnology
    extra = 1


@admin.register(ServiceProcess)
class ServiceProcessAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "img")

    def has_module_permission(self, request):
        return False


class ServiceContentAdmin(admin.StackedInline):
    model = ServiceContent
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order", "active")
    search_fields = ("title",)
    inlines = (ServiceTechnologyInline, ServiceContentAdmin)

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


class BlogContextInline(admin.StackedInline):
    model = BlogContext
    extra = 1




class BlogFAQInline(admin.TabularInline):
    model = BlogFAQ
    extra = 1


class BlogModeratorFeedbackInline(admin.StackedInline):
    model = BlogModeratorFeedback
    extra = 1
    # formset = BlogModeratorFeedbackFormSet
    fields = ("created_by_title", "feedback")
    readonly_fields = ("created_by_title",)

class BlogForm(forms.ModelForm):
    
    class Meta:
        model = Blog
        fields = "__all__"
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.request.user.is_superuser and not self.request.user.has_perm("website.can_approve"):
            self.fields["status"].choices = (('pending', 'Pending'), ('moderator', 'Moderator'))


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

    inlines = (BlogContextInline, BlogFAQInline, BlogModeratorFeedbackInline)
    actions = ["clone_selected", "approve_selected", "unapprove_selected"]

    search_fields = ("title",)
    autocomplete_fields = ["category", "tag"]
    list_display = (
        "title",
        "author",
        "slug",
        "created_at",
        "updated_at",
        "active",
        "status",
    )
    fields = (
        "title",
        "slug",
        "image",
        "video",
        "youtube_link",
        "category",
        "tag",
        "short_description",
        "is_featured",
        "content",
        "read_time_minute",
        "total_view",
        "status",
    )
    form = BlogForm
    list_filter = ("status", )
    class Media:
        js = ("js/blog_post_field_escape.js",)

    @admin.action(description="Deactivate selected blogs")
    def unapprove_selected(self, request, queryset):
        queryset.update(active=False)
        self.message_user(request, f"Successfully unapproved {queryset.count()} blogs.")

    # list_editable = ("active", "approved",)

    @admin.action(description="Activate selected blogs")
    def approve_selected(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, f"Successfully approved {queryset.count()} blogs.")

    @admin.action(description="Clone selected blogs")
    def clone_selected(self, request, queryset):
        cloned_blogs = []

        with transaction.atomic():
            for index, blog in enumerate(queryset, start=1):
                # Create a copy of the blog with a new ID and reset some fields
                cloned_blog_data = model_to_dict(
                    blog,
                    exclude=[
                        "id",
                        "pk",
                        "slug",
                        "category",
                        "tag",
                        "created_at",
                        "updated_at",
                    ],
                )

                cloned_blog = Blog(**cloned_blog_data)

                new_title = blog.title
                if len(new_title) > 247:
                    new_title = new_title[0:245]

                # Process title
                cloned_blog.title = f"Copy of {new_title}"

                # Process slug
                cloned_blog.slug = blog.slug

                suffix = 1
                while Blog.objects.filter(slug=cloned_blog.slug).exists():
                    cloned_blog.slug = f"{cloned_blog.slug}-{suffix}"
                    suffix += 1

                cloned_blog.created_by = request.user
                cloned_blog.created_at = timezone.now()
                cloned_blog.updated_at = timezone.now()
                cloned_blog.save()  # Save the cloned blog first to get an ID

                for context in blog.blog_contexts.all():
                    blogcontext = BlogContext()
                    blogcontext.blog = cloned_blog
                    blogcontext.title = context.title
                    blogcontext.description = context.description
                    blogcontext.image = context.image
                    blogcontext.video = context.video
                    blogcontext.save()

                # Now, add the many-to-many relationships
                for category in blog.category.all():
                    cloned_blog.category.add(category)

                for tag in blog.tag.all():
                    cloned_blog.tag.add(tag)

                cloned_blogs.append(cloned_blog)

        self.message_user(request, f"Successfully cloned {len(cloned_blogs)} blogs.")

    @admin.display(description="Created By")
    def author(self, obj):
        author = obj.created_by
        return f"{author.first_name} {author.last_name}"

    def get_actions(self, request):
        actions = super().get_actions(request)

        # Check if the user has the 'can_approve' permission
        if not request.user.has_perm("website.can_approve"):
            # If the user doesn't have permission, remove the 'approve_selected' action
            del actions["approve_selected"]
            del actions["unapprove_selected"]

        return actions

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        querySet = super().get_queryset(request)
        user = request.user
        if user.has_perm("website.can_view_all"):
            return querySet
        else:
            return querySet.filter(created_by=user)

    def get_form(
        self,
        request: Any,
        obj: Union[Any, None] = ...,
        change: bool = ...,
        **kwargs: Any,
    ) -> Any:
        form = super().get_form(request, obj, change, **kwargs)
        form.request = request
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
        return super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for inline_form in formset.forms:
                if (
                    inline_form._meta.model == BlogModeratorFeedback
                    and inline_form.instance.id is None
                    and inline_form.cleaned_data
                ):
                    if request.user.has_perm("website.can_approve"):
                        content = inline_form.cleaned_data.get("feedback")
                        blog = inline_form.cleaned_data.get("blog")
                        async_task(
                            "website.tasks.send_blog_moderator_feedback_email",
                            content,
                            blog.created_by.employee,
                        )

        return super().save_related(request, form, formsets, change)


@admin.register(BlogComment)
class BlogCommentModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ["id", "name"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    model = FAQ
    list_display = ["question", "answer"]


@admin.register(OurAchievement)
class OurAchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "number")

    def has_module_permission(self, request):
        return False


@admin.register(OurGrowth)
class OurGrowthAdmin(admin.ModelAdmin):
    list_display = ("title", "number")

    def has_module_permission(self, request):
        return False


@admin.register(OurJourney)
class OurJourneyAdmin(admin.ModelAdmin):
    list_display = ("year", "title", "description", "img")

    def has_module_permission(self, request):
        return False


@admin.register(EmployeePerspective)
class EmployeePerspectiveAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "title",
        "description",
    )


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("title", "short_description")
    search_fields = ("title", "short_description")
    filter_horizontal = ("technology",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("technology")

    def has_module_permission(self, request):
        return False


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "message")
    search_fields = ("name", "email")
    list_filter = ("name", "email")
    ordering = ("name",)
    fields = ("name", "email", "message")
    # date_hierarchy = "created_at"


@admin.register(VideoTestimonial)
class VideoTestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "designation", "country")
    search_fields = ("name", "designation")
    list_filter = ("name", "country")
    ordering = ("name",)
    # date_hierarchy = "created_at"


@admin.register(IndustryWeServe)
class IndustryWeServeAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_module_permission(self, request):
        return False


@admin.register(LifeAtMediusware)
class LifeAtMediuswareAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
