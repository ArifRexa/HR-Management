from typing import Any, Union
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils import timezone
from mptt.admin import MPTTModelAdmin
from django.utils.html import format_html
from django.db import transaction
from django.forms.models import model_to_dict
import requests

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
    FAQ,
    ServiceTechnology,
    ServiceProcess,
    OurAchievement,
    OurGrowth,
    OurJourney
)


class ServiceTechnologyInline(admin.TabularInline):
    model =  ServiceTechnology
    extra = 1

@admin.register(ServiceProcess)
class ServiceProcessAdmin(admin.ModelAdmin):
    list_display = ("title","description","img")



    def has_module_permission(self, request):
        return False

    

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order", "active")
    search_fields = ("title",)
    inlines = (ServiceTechnologyInline,)
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
    actions = ['clone_selected', 'approve_selected', 'unapprove_selected']

    search_fields = ("title",)
    autocomplete_fields = ["category", "tag"]
    list_display = (
        "title",
        "author",
        "slug",
        "created_at",
        "updated_at",
        "active",
        # "approved",
    )


    @admin.action(description='Deactivate selected blogs')
    def unapprove_selected(self, request, queryset):
        queryset.update(active=False)
        self.message_user(request, f'Successfully unapproved {queryset.count()} blogs.')

    # list_editable = ("active", "approved",)

    @admin.action(description='Activate selected blogs')
    def approve_selected(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, f'Successfully approved {queryset.count()} blogs.')



    @admin.action(description='Clone selected blogs')
    def clone_selected(self, request, queryset):
        cloned_blogs = []

        with transaction.atomic():
            for index, blog in enumerate(queryset, start=1):
                # Create a copy of the blog with a new ID and reset some fields
                cloned_blog_data = model_to_dict(blog, exclude=['id', 'pk', 'slug', 'category', 'tag', 'created_at', 'updated_at'])

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

        self.message_user(request, f'Successfully cloned {len(cloned_blogs)} blogs.')


    @admin.display(description="Created By")
    def author(self, obj):
        author = obj.created_by
        return f"{author.first_name} {author.last_name}"

    def get_actions(self, request):
        actions = super().get_actions(request)
        
        # Check if the user has the 'can_approve' permission
        if not request.user.has_perm('website.can_approve'):
            # If the user doesn't have permission, remove the 'approve_selected' action
            del actions['approve_selected']
            del actions['unapprove_selected']
            
        return actions

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


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    model = FAQ
    list_display = ["question","answer"]

@admin.register(OurAchievement)
class OurAchievementAdmin(admin.ModelAdmin):
    list_display = ("title","number")
    
    def has_module_permission(self, request):
        return False
    

@admin.register(OurGrowth)
class OurGrowthAdmin(admin.ModelAdmin):
    list_display = ("title","number")
    
    def has_module_permission(self, request):
        return False


@admin.register(OurJourney)
class OurJourneyAdmin(admin.ModelAdmin):
    list_display = ("year","title","description","img")

    def has_module_permission(self,request):
        return False


