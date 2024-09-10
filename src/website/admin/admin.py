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
from django.urls import reverse
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.db.models import Count

# Register your models here.
from employee.models.employee import Employee
from project_management.models import (
    EmployeeProjectHour,
    ProjectHour,
    ProjectServiceSolution,
)
from website.models import (
    AllProjectsBanner,
    Award,
    AwardsBanner,
    BannerImage,
    BlogFAQ,
    BlogModeratorFeedback,
    BlogStatus,
    CSRBanner,
    ClientTestimonialBanner,
    ClutchTestimonialBanner,
    ContactBanner,
    DeliveryModelBanner,
    DevelopmentMethodologyBanner,
    EngagementModelBanner,
    Gallery,
    HomeBanner,
    IndustryWeServe,
    LifeAtMediusware,
    ModelTitle,
    OfficeLocation,
    PageBanner,
    PostCredential,
    PostPlatform,
    ProjectClientReviewTitle,
    ProjectKeyFeatureTitle,
    ProjectResultsTitle,
    ProjectScreenshotTitle,
    ProjectServiceSolutionTitle,
    ProjectTechnologyTitle,
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
    Brand,
    WebsiteTitle,
    AwardsTitle,
    WhyUsTitle,
    AllServicesTitle,
    TechnologyTitle,
    VideoTestimonialTitle,
    IndustryTitle,
    LifeAtMediuswareTitle,
    ProjectsVideoTitle,
    BlogTitle,
    TextualTestimonialTitle,
    SpecialProjectsTitle,
    FAQHomeTitle,
    OurJourneyTitle,
    WhyWeAreBanner,
    WomenEmpowermentBanner,
)

from website.linkedin_post import automatic_blog_post_linkedin


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
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def has_module_permission(self, request):
        return False


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
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


class BlogContextForm(forms.ModelForm):
    class Meta:
        model = BlogContext
        fields = "__all__"
        widgets = {
            "title": forms.Textarea(
                attrs={"rows": 2, "cols": 40, "style": "width: 70%;resize:none;"}
            ),
        }


class BlogContextInline(admin.StackedInline):
    model = BlogContext
    extra = 1
    form = BlogContextForm


class BlogFAQForm(forms.ModelForm):
    class Meta:
        model = BlogFAQ
        fields = ("question", "answer")
        widgets = {
            "question": forms.Textarea(
                attrs={"rows": 2, "cols": 40, "style": "width: 95%;resize:none;"}
            ),
            "answer": forms.Textarea(attrs={"style": "width: 95%;"}),
        }


class BlogFaqFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        valid_forms_count = 0
        if not self.request.user.is_superuser and not self.request.user.has_perm(
            "website.can_approve"
        ):
            for form in self.forms:
                # Check if the form has valid data and is not marked for deletion
                if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                    # Skip forms that are completely empty
                    if any(
                        field for field in form.cleaned_data if form.cleaned_data[field]
                    ):
                        valid_forms_count += 1

            if valid_forms_count < 3:
                raise ValidationError("You must create at least 3 FAQ.")


class BlogFAQInline(admin.TabularInline):
    model = BlogFAQ
    extra = 1
    form = BlogFAQForm
    verbose_name_plural = "Blog FAQs(NB:Minimum 3 faq required)"
    formset = BlogFaqFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset


class BlogModeratorFeedbackInline(admin.StackedInline):
    model = BlogModeratorFeedback
    extra = 1
    # formset = BlogModeratorFeedbackFormSet
    fields = ("created_by_title", "feedback")
    readonly_fields = ("created_by_title",)


class BlogForm(forms.ModelForm):
    next_status = forms.ChoiceField(choices=BlogStatus.choices[:-1], required=False)

    class Meta:
        model = Blog
        fields = "__all__"
        widgets = {
            "title": forms.Textarea(
                attrs={"rows": 2, "cols": 40, "style": "width: 70%;resize:none;"}
            ),
            "content": forms.Textarea(attrs={"rows": 20, "style": "width: 80%;"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.fields:
            if not self.request.user.is_superuser and not self.request.user.has_perm(
                "website.can_approve"
            ):
                self.fields["next_status"].choices = (
                    ("draft", "In Draft"),
                    ("submit_for_review", "In Review"),
                )
            elif not self.request.user.is_superuser and self.request.user.has_perm(
                "website.can_approve"
            ):
                # if (self.change and self.instance.created_by == self.request.user) or not self.change:
                #     pass
                # else:

                self.fields["next_status"].choices = (
                    ("need_revision", "In Revision"),
                    ("approved", "Approved"),
                )

    def save(self, commit=True):
        from django.utils.text import slugify

        if self.cleaned_data.get("next_status"):
            self.instance.status = self.cleaned_data["next_status"]
        if not self.instance.slug:
            self.instance.slug = slugify(self.cleaned_data["title"])[:50]
        if self.request.user.is_superuser or self.request.user.has_perm(
            "website.can_approve"
        ):
            if self.cleaned_data.get("next_status") == "approved":
                self.instance.active = True
        return super().save(commit)


class ActiveEmployeeFilter(admin.SimpleListFilter):
    title = "Author"
    parameter_name = "created_by__employee__id__exact"

    def lookups(self, request, model_admin):
        employees = (
            Employee.objects.filter(active=True)
            .annotate(total_blog=Count("user__website_blog_related"))
            .distinct()
        )
        looksup_list = []
        for employee in list(employees):
            if employee.total_blog == 0:
                looksup_list.append((employee.pk, employee.full_name))
            else:
                looksup_list.append(
                    (employee.pk, f"{employee.full_name} ({employee.total_blog})")
                )
        return tuple(looksup_list)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created_by__employee__id__exact=self.value())
        return queryset


class BlogCategoryFilter(admin.SimpleListFilter):
    title = "Category"
    parameter_name = "category__id__exact"

    def lookups(self, request, model_admin):
        categories = Category.objects.annotate(total_blog=Count("categories")).all()
        lookup_list = []
        for category in list(categories):
            if category.total_blog == 0:
                lookup_list.append((category.pk, category.name))
            else:
                lookup_list.append(
                    (category.pk, f"{category.name} ({category.total_blog})")
                )
        return tuple(lookup_list)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__id__exact=self.value())
        return queryset


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    # prepopulated_fields = {"slug": ("title",)}

    inlines = (BlogContextInline, BlogFAQInline, BlogModeratorFeedbackInline)
    actions = [
        "clone_selected",
        "draft_selected",
        "in_revision_selected",
        "submit_for_review_selected",
        "approve_selected",
    ]

    search_fields = ("title",)
    autocomplete_fields = ["category", "tag"]
    list_display = (
        "title",
        "author",
        "created_at",
        "updated_at",
        "status",
    )
    readonly_fields = ("status",)
    exclude = ("slug",)
    fields = (
        "title",
        "image",
        # "video",
        "youtube_link",
        "category",
        "tag",
        # "short_description",
        "is_featured",
        "content",
        "read_time_minute",
        "status",
        "next_status",
    )
    form = BlogForm
    list_filter = ("status", BlogCategoryFilter, ActiveEmployeeFilter)

    class Media:
        js = ("js/blog_post_field_escape.js",)

    # @admin.action(description="Deactivate selected blogs")
    # def unapprove_selected(self, request, queryset):
    #     queryset.update(status=)
    #     self.message_user(request, f"Successfully unapproved {queryset.count()} blogs.")

    # list_editable = ("active", "approved",)
    def lookup_allowed(self, lookup, value):
        if lookup in ["created_by__employee__id__exact"]:
            return True
        return super().lookup_allowed(lookup, value)

    @admin.action(description="Change Status In To Approved")
    def approve_selected(self, request, queryset):
        queryset.update(status=BlogStatus.APPROVED, approved_at=timezone.now())
        self.message_user(request, f"Successfully approved {queryset.count()} blogs.")

    @admin.action(description="Change Status In To Draft")
    def draft_selected(self, request, queryset):
        queryset.update(status=BlogStatus.DRAFT, approved_at=None)
        self.message_user(request, f"Successfully updated {queryset.count()} blogs.")

    @admin.action(description="Change Status In To Revision")
    def in_revision_selected(self, request, queryset):
        queryset.update(status=BlogStatus.NEED_REVISION, approved_at=None)
        self.message_user(request, f"Successfully updated {queryset.count()} blogs.")

    @admin.action(description="Change Status In To Review")
    def submit_for_review_selected(self, request, queryset):
        queryset.update(status=BlogStatus.SUBMIT_FOR_REVIEW, approved_at=None)
        self.message_user(request, f"Successfully updated {queryset.count()} blogs.")

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
            del actions["in_revision_selected"]

        return actions

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        querySet = super().get_queryset(request)
        user = request.user
        if user.has_perm("website.can_view_all"):
            return querySet
        else:
            return querySet.filter(created_by=user)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        form.change = obj is not None
        return form

    def get_fields(self, request, obj):
        fields = super().get_fields(request, obj)
        fields = list(fields)
        if not request.user.is_superuser and not request.user.has_perm(
            "website.can_approve"
        ):
            fields.remove("is_featured")
            fields.remove("content")
        return fields

    def has_change_permission(self, request, obj=None):
        permitted = super().has_change_permission(request, obj=obj)
        # print(request.user.has_perm("website.can_change_after_approve"))
        if permitted and request.user.has_perm("website.can_change_after_approve"):
            return True

        if permitted and obj:
            author_permission = (
                not obj.status == BlogStatus.APPROVED and obj.created_by == request.user
            )
            moderator_permission = (
                not obj.status == BlogStatus.APPROVED
                and request.user.has_perm("website.can_approve")
            )
            return author_permission or moderator_permission
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Union[Any, None] = ...
    ) -> bool:
        permitted = super().has_delete_permission(request, obj)
        user = request.user
        if permitted and user.has_perm("website.can_delete_after_approve"):
            return True
        elif permitted and isinstance(obj, Blog):
            return not obj.status == BlogStatus.APPROVED and obj.created_by == user
        return permitted

    def get_urls(self):
        from functools import update_wrapper
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urls = super(BlogAdmin, self).get_urls()

        automate_post_urls = [
            path("automate-post/", wrap(self.automate_post_view), name="automate_post"),
        ]
        return automate_post_urls + urls

    def automate_post_view(self, request, *args, **kwargs):
        from django.template.response import TemplateResponse

        linkedin_token = PostCredential.objects.filter(
            platform=PostPlatform.LINKEDIN
        ).first()
        context = dict(
            self.admin_site.each_context(request),
            linkedin_token=linkedin_token.token if linkedin_token else None,
            posted=Blog.objects.filter(status=BlogStatus.PUBLISHED).count(),
            in_queue=Blog.objects.filter(status=BlogStatus.APPROVED).count(),
        )
        return TemplateResponse(request, "blog/automate_post.html", context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj and obj.status == BlogStatus.APPROVED:
            if request.user.is_superuser or request.user.has_perm(
                "website.can_approve"
            ):
                publish_blog_url = f"https://mediusware.com/blog/details/{obj.slug}/"
                obj.approved_at = timezone.now()
                obj.save()
                async_task(
                    "website.tasks.thank_you_message_to_author",
                    obj,
                    publish_blog_url,
                )
                # automatic_blog_post_linkedin()
                project_hour = ProjectHour.objects.create(
                    project_id=20,
                    manager_id=30,
                    hour_type="bonus",
                    date=timezone.now().date(),
                    hours=30,
                    status="approved",
                )
                employee_hour = EmployeeProjectHour.objects.create(
                    project_hour=project_hour,
                    employee=obj.created_by.employee,
                    hours=30,
                )
                print(project_hour, employee_hour)
        else:
            obj.approved_at = None
            obj.save()

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for inline_form in formset.forms:
                if (
                    inline_form._meta.model == BlogModeratorFeedback
                    and inline_form.instance.id is None
                    and inline_form.cleaned_data
                ):
                    if request.user.is_superuser or request.user.has_perm(
                        "website.can_approve"
                    ):
                        content = inline_form.cleaned_data.get("feedback")
                        blog = inline_form.cleaned_data.get("blog")
                        blog_url = request.build_absolute_uri(
                            reverse("admin:website_blog_change", args=[blog.id])
                        )
                        async_task(
                            "website.tasks.send_blog_moderator_feedback_email",
                            content,
                            blog,
                            blog_url,
                        )
        super().save_related(request, form, formsets, change)


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


@admin.register(OfficeLocation)
class OfficeLocationAdmin(admin.ModelAdmin):
    list_display = (
        "office",
        "address",
        "contact",
    )

    def has_module_permission(self, request):
        return False


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "brandphoto")


# Inline classes for each model
class AwardsTitleInline(admin.StackedInline):
    model = AwardsTitle
    can_delete = False
    extra = 1


class WhyUsTitleInline(admin.StackedInline):
    model = WhyUsTitle
    can_delete = False
    extra = 1


class AllServicesTitleInline(admin.StackedInline):
    model = AllServicesTitle
    can_delete = False
    extra = 1


class TechnologyTitleInline(admin.StackedInline):
    model = TechnologyTitle
    can_delete = False
    extra = 1


class VideoTestimonialTitleInline(admin.StackedInline):
    model = VideoTestimonialTitle
    can_delete = False
    extra = 1


class IndustryTitleInline(admin.StackedInline):
    model = IndustryTitle
    can_delete = False
    extra = 1


class LifeAtMediuswareTitleInline(admin.StackedInline):
    model = LifeAtMediuswareTitle
    can_delete = False
    extra = 1


class ProjectsVideoTitleInline(admin.StackedInline):
    model = ProjectsVideoTitle
    can_delete = False
    extra = 1


class BlogTitleInline(admin.StackedInline):
    model = BlogTitle
    can_delete = False
    extra = 1


class TextualTestimonialTitleInline(admin.StackedInline):
    model = TextualTestimonialTitle
    can_delete = False
    extra = 1


class SpecialProjectsTitleInline(admin.StackedInline):
    model = SpecialProjectsTitle
    can_delete = False
    extra = 1


class FAQHomeTitleInline(admin.StackedInline):
    model = FAQHomeTitle
    can_delete = False
    extra = 1


class OurJourneyTitleInline(admin.StackedInline):
    model = OurJourneyTitle
    can_delete = False
    extra = 1


class ModelTitleInline(admin.StackedInline):
    model = ModelTitle
    can_delete = False
    extra = 1


class ProjectServiceSolutionInline(admin.StackedInline):
    model = ProjectServiceSolutionTitle
    can_delete = False
    extra = 1


class ProjectKeyFeatureTitleInline(admin.StackedInline):
    model = ProjectKeyFeatureTitle
    can_delete = False
    extra = 1


class ProjectScreenshotTitleInline(admin.StackedInline):
    model = ProjectScreenshotTitle
    can_delete = False
    extra = 1


class ProjectResultsTitleInline(admin.StackedInline):
    model = ProjectResultsTitle
    can_delete = False
    extra = 1


class ProjectTechnologyTitleInline(admin.StackedInline):
    model = ProjectTechnologyTitle
    can_delete = False
    extra = 1


class ProjectClientReviewTitleInline(admin.StackedInline):
    model = ProjectClientReviewTitle
    can_delete = False
    extra = 1


# Register the WebsiteTitle admin with all the inlines
@admin.register(WebsiteTitle)
class WebsiteTitleAdmin(admin.ModelAdmin):
    inlines = [
        AwardsTitleInline,
        WhyUsTitleInline,
        AllServicesTitleInline,
        TechnologyTitleInline,
        VideoTestimonialTitleInline,
        IndustryTitleInline,
        LifeAtMediuswareTitleInline,
        ProjectsVideoTitleInline,
        BlogTitleInline,
        TextualTestimonialTitleInline,
        SpecialProjectsTitleInline,
        ModelTitleInline,
        FAQHomeTitleInline,
        OurJourneyTitleInline,
        ProjectClientReviewTitleInline,
        ProjectKeyFeatureTitleInline,
        ProjectScreenshotTitleInline,
        ProjectResultsTitleInline,
        ProjectServiceSolutionInline,
        ProjectTechnologyTitleInline,
    ]


class BaseInline(admin.StackedInline):
    can_delete = False
    extra = 1


class HomeBannerBannerInline(BaseInline):
    model = HomeBanner
    verbose_name = "Home Banner"


# why we are, women empowerment, csr, delivery model, engagement model, development methodology, client testimonial, clutch testimonials, awards, contact
class WhyWeAreBannerInline(BaseInline):
    model = WhyWeAreBanner
    verbose_name = "Why We Are Banner"


class WomenEmpowermentBannerInline(BaseInline):
    model = WomenEmpowermentBanner
    verbose_name = "Women Empowerment Banner"


class CSRBannerInline(BaseInline):
    model = CSRBanner
    verbose_name = "CSR Banner"


class DeliveryModelBannerInline(BaseInline):
    model = DeliveryModelBanner
    verbose_name = "Delivery Model Banner"


class EngagementModelBannerInline(BaseInline):
    model = EngagementModelBanner
    verbose_name = "Engagement Model Banner"


class DevelopmentMethodologyBannerInline(BaseInline):
    model = DevelopmentMethodologyBanner
    verbose_name = "Development Methodology Banner"


class ClientTestimonialBannerInline(BaseInline):
    model = ClientTestimonialBanner
    verbose_name = "Client Testimonial Banner"


class ClutchTestimonialBannerInline(BaseInline):
    model = ClutchTestimonialBanner
    verbose_name = "Clutch Testimonial Banner"


class AwardsBannerInline(BaseInline):
    model = AwardsBanner
    verbose_name = "Awards Banner"


class ContactBannerInline(BaseInline):
    model = ContactBanner
    verbose_name = "Contact Banner"


class AllProjectsBannerInline(BaseInline):
    model = AllProjectsBanner
    verbose_name = "All Projects Banner"


@admin.register(PageBanner)
class PageBannerAdmin(admin.ModelAdmin):
    inlines = [
        HomeBannerBannerInline,
        WhyWeAreBannerInline,
        WomenEmpowermentBannerInline,
        CSRBannerInline,
        DeliveryModelBannerInline,
        EngagementModelBannerInline,
        DevelopmentMethodologyBannerInline,
        ClientTestimonialBannerInline,
        ClutchTestimonialBannerInline,
        AwardsBannerInline,
        ContactBannerInline,
        AllProjectsBannerInline,
    ]
