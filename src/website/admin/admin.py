from html import escape
import json
from typing import Any, Union

import nested_admin
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count
from django.db.models.query import QuerySet
from django.forms.models import BaseInlineFormSet, model_to_dict
from django.http.request import HttpRequest
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django_q.tasks import async_task
from mptt.admin import MPTTModelAdmin
from django.contrib.admin import SimpleListFilter

# Register your models here.
from employee.models.employee import Employee
from project_management.models import ProjectHour
from website.admin.industries_we_serve import ApplicationAreasInline, IndustryMetadataInline
from website.admin.services import AdditionalServiceContentInline, ComparativeAnalysisInline, DevelopmentServiceProcessInline, DiscoverOurServiceInline, ServiceMetaDataInline
from website.models import (
    CTA,
    FAQ,
    AdditionalPageFAQ,
    AdditionalPageHeroSection,
    AdditionalPageKeyThings,
    AdditionalPageKeyThingsCards,
    AdditionalPageOurProcess,
    AdditionalPageWhyChooseUs,
    AdditionalPages,
    AllProjectsBanner,
    AllServicesTitle,
    ArchivePage,
    Award,
    AwardCategory,
    AwardYearGroup,
    Awards,
    AwardsBanner,
    AwardsTitle,
    BenefitsOfEmployment,
    BenefitsOfEmploymentTitle,
    Blog,
    BlogCategory,
    BlogComment,
    BlogContext,
    BlogFAQ,
    BlogFAQSchema,
    BlogKeyword,
    BlogMeatadata,
    BlogModeratorFeedback,
    BlogSEOEssential,
    BlogStatus,
    BlogTag,
    BlogTitle,
    Brand,
    Career,
    CareerBanner,
    Category,
    Certification,
    ClientTestimonialBanner,
    ClutchTestimonialBanner,
    ContactBanner,
    ContactForm,
    CSRBanner,
    DeliveryModelBanner,
    DevelopmentMethodologyBanner,
    EcoSystem,
    EcoSystemCardTags,
    EcoSystemCards,
    EmployeePerspective,
    EmployeeTestimonial,
    EmployeeTestimonialTitle,
    EngagementModelBanner,
    EventCalender,
    FAQHomeTitle,
    Gallery,
    HistoryOfTech,
    HomeBanner,
    Industry,
    IndustryTitle,
    IndustryWeServe,
    Lead,
    Leadership,
    LeaderShipBanner,
    LeadershipSpeech,
    LifeAtMediusware,
    LifeAtMediuswareTitle,
    ModelTitle,
    OfficeLocation,
    OurAchievement,
    OurGrowth,
    OurJourney,
    OurJourneyTitle,
    PageBanner,
    PlagiarismInfo,
    PostCredential,
    PostPlatform,
    ProjectClientReviewTitle,
    ProjectKeyFeatureTitle,
    ProjectResultsTitle,
    ProjectScreenshotTitle,
    ProjectServiceSolutionTitle,
    ProjectsVideoTitle,
    ProjectTechnologyTitle,
    PublicImage,
    ReferenceBlogs,
    RelatedBlogs,
    Service,
    ServiceContent,
    ServiceKeyword,
    ServiceMeatadata,
    ServiceProcess,
    ServiceTechnology,
    ServicesWeProvide,
    ServicesWeProvideCards,
    SpecialProjectsTitle,
    Tag,
    TeamElement,
    Technology,
    TechnologyCTA,
    TechnologyCreatorsQuotes,
    TechnologyFAQ,
    TechnologyFAQSchema,
    TechnologyKeyThings,
    TechnologyKeyThingsQA,
    TechnologyMetaData,
    TechnologyOurProcess,
    TechnologySolutionsAndServices,
    TechnologySolutionsAndServicesCards,
    TechnologyTitle,
    TechnologyType,
    TechnologyWhyChooseUs,
    TechnologyWhyChooseUsCards,
    TechnologyWhyChooseUsCardsDetails,
    TextualTestimonialTitle,
    VideoTestimonial,
    VideoTestimonialTitle,
    WebsiteTitle,
    WhatIs,
    WhyUsTitle,
    WhyWeAreBanner,
    WomenEmpowermentBanner,
)
from website.models_v2.industries_we_serve import Benefits, BenefitsQA, CustomSolutions, CustomSolutionsCards, IndustryDetailsHeading, IndustryDetailsHeadingCards, IndustryDetailsHeroSection, IndustryItemTags, OurProcess, ServeCategory, ServeCategoryCTA, ServeCategoryFAQSchema, ServiceCategoryFAQ, WhyChooseUs, WhyChooseUsCards, WhyChooseUsCardsDetails
from website.models_v2.services import BestPracticesCards, BestPracticesCardsDetails, BestPracticesHeadings, KeyThings, KeyThingsQA, MetaDescription, ServiceFAQQuestion, ServicePage, ServicePageCTA, ServicePageFAQSchema, ServicesItemTags, ServicesOurProcess, ServicesRelatedBlogs, ServicesWhyChooseUs, ServicesWhyChooseUsCards, ServicesWhyChooseUsCardsDetails, SolutionsAndServices, SolutionsAndServicesCards
from website.utils.plagiarism_checker import check_plagiarism


class ServiceKeywordInline(nested_admin.NestedTabularInline):
    model = ServiceKeyword
    extra = 1


class ServiceMetadataInline(nested_admin.NestedStackedInline):
    model = ServiceMeatadata
    extra = 1
    inlines = [ServiceKeywordInline]


class BlogKeywordInline(nested_admin.NestedTabularInline):
    model = BlogKeyword
    extra = 1


class BlogMetadataInline(nested_admin.NestedStackedInline):
    model = BlogMeatadata
    extra = 1
    inlines = [BlogKeywordInline]


# class UserAdmin(BaseUserAdmin):
#     class Media:
#         js = ("js/custom_permission_search.js",)
# css = {"all": ("css/user.css",)}


class GroupAdmin(BaseGroupAdmin):
    class Media:
        js = ("js/custom_permission_search.js",)
        css = {"all": ("css/user.css",)}


# Unregister the existing User admin
# admin.site.unregister(User)
admin.site.unregister(Group)

# Register the customized User admin
# admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ["title", "image", "short_description"]

    def has_module_permission(self, request):
        return False


# @admin.register(Gallery)
# class GalleryAdmin(admin.ModelAdmin):
#     list_display = ["image"]


class ServiceTechnologyInline(nested_admin.NestedTabularInline):
    model = ServiceTechnology
    extra = 1


@admin.register(ServiceProcess)
class ServiceProcessAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "img")

    def has_module_permission(self, request):
        return False


class ServiceContentAdmin(nested_admin.NestedTabularInline):
    model = ServiceContent
    extra = 1


@admin.register(Service)
class ServiceAdmin(nested_admin.NestedModelAdmin):
    list_display = ("title", "slug", "order", "active")
    search_fields = ("title",)
    inlines = (ServiceTechnologyInline, ServiceContentAdmin, ServiceMetadataInline)

    def has_module_permission(self, request):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    # def has_module_permission(self, request):
    #     return False


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


class BlogContextInline(nested_admin.NestedStackedInline):
    model = BlogContext
    extra = 1
    form = BlogContextForm
    verbose_name = "Blog Section"
    verbose_name_plural = "Blog Sections"


class BlogFAQForm(forms.ModelForm):
    class Meta:
        model = BlogFAQ
        fields = ("question", "answer")
        widgets = {
            "question": forms.Textarea(
                attrs={"rows": 2, "style": "width: 85%;"}
            ),
            # "answer": forms.Textarea(attrs={"style": "width: 95%;"}),
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


class BlogFAQInline(nested_admin.NestedStackedInline):
    model = BlogFAQ
    extra = 1
    form = BlogFAQForm
    verbose_name_plural = "Blog FAQ (NB: Minimum 3 FAQs required)"
    formset = BlogFaqFormSet
    fields = ("question", "answer")

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

class BlogFAQSchemaInline(nested_admin.NestedStackedInline):
    model = BlogFAQSchema
    extra = 0
    fields = ("faq_schema",)
    # readonly_fields = ("faq_schema",)
    can_delete = False
    max_num = 1
    verbose_name = "FAQ Schema"
    verbose_name_plural = "FAQ Schema"

class RelatedBlogInline(nested_admin.NestedStackedInline):
    model = RelatedBlogs
    fields = ["releted_blog"]
    autocomplete_fields = ["releted_blog"]
    extra = 0
    fk_name = "blog"


class ReferenceBlogInline(nested_admin.NestedStackedInline):
    model = ReferenceBlogs
    fields = ["blog", "reference_blog_title", "reference_blog_link"]
    extra = 0


class BlogModeratorFeedbackInline(nested_admin.NestedStackedInline):
    model = BlogModeratorFeedback
    extra = 1
    fields = ("created_by_title", "feedback")
    readonly_fields = ("created_by_title",)


class BlogForm(forms.ModelForm):
    next_status = forms.ChoiceField(choices=[('', 'Select option')] + BlogStatus.choices[:-1], required=False, label="Status")
    
    class Meta:
        model = Blog
        fields = "__all__"
        widgets = {
            "title": forms.Textarea(attrs={"rows": 2, "cols": 40, "style": "width: 70%;resize:none;"}),
            "slug": forms.Textarea(attrs={"rows": 2, "cols": 40, "style": "width: 70%;resize:none;"}),
            "content": forms.Textarea(attrs={"rows": 20, "style": "width: 80%;"}),
            "main_body_schema": forms.Textarea(attrs={"rows": 10, "cols": 80}),
            "parent_services": admin.widgets.AutocompleteSelectMultiple(
                Blog._meta.get_field('parent_services'),
                admin.site,
                # attrs={'style': 'width: 45%; display: inline-block;'}
            ),
            # "child_services": admin.widgets.AutocompleteSelectMultiple(
            #     Blog._meta.get_field('child_services'),
            #     admin.site,
            #     # attrs={'style': 'width: 45%; display: inline-block; margin-left: 10px;'}
            # ),
        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['parent_services'].queryset = ServicePage.objects.filter(is_parent=True)
        # self.fields['child_services'].queryset = ServicePage.objects.filter(is_parent=False)
        if self.instance and self.instance.pk:
            self.fields['next_status'].initial = self.instance.status
            self.fields['parent_services'].initial = self.instance.parent_services.all()
            # self.fields['child_services'].initial = self.instance.child_services.all()
        if self.request and hasattr(self.request, 'user'):
            if not self.request.user.is_superuser and not self.request.user.has_perm("website.can_approve"):
                self.fields["next_status"].choices = [('', 'Select option'), ("draft", "In Draft"), ("submit_for_review", "In Review")]
                self.fields["main_body_schema"].widget.attrs['readonly'] = True
            elif not self.request.user.is_superuser and self.request.user.has_perm("website.can_approve"):
                self.fields["next_status"].choices = [('', 'Select option'), ("need_revision", "In Revision"), ("approved", "Approved")]
        self.fields['parent_services'].queryset = ServicePage.objects.filter(is_parent=True)
    
    # def save(self, commit=True):
    #     from django.utils.text import slugify
    #     if self.cleaned_data.get("next_status"):
    #         self.instance.status = self.cleaned_data["next_status"]
    #     if not self.instance.slug:
    #         self.instance.slug = slugify(self.cleaned_data["title"])[:50]
    #     return super().save(commit)

    def save(self, commit=True):
        from django.utils.text import slugify
        if self.cleaned_data.get("next_status"):
            self.instance.status = self.cleaned_data["next_status"]
        if not self.instance.slug:
            self.instance.slug = slugify(self.cleaned_data["title"])[:50]
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.instance.parent_services.set(self.cleaned_data['parent_services'])
            self.instance.child_services.set(self.cleaned_data['child_services'])
            self.save_m2m()
        return instance



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


class BlogSEOEssentialForm(forms.ModelForm):
    class Meta:
        model = BlogSEOEssential
        fields = "__all__"

        widgets = {
            "keywords": forms.Textarea(
                attrs={
                    "placeholder": "Enter keywords inside square brackets separated by commas e.g [Keyword1, Keyword2]",
                    "rows": 10,
                    "cols": 40,
                    "class": "vLargeTextField",
                    # "style": "width: 95%;resize:none;",
                }
            )
        }

        
class CTAInline(nested_admin.NestedStackedInline):
    model = CTA
    extra = 1
    verbose_name = "Call to Action"
    verbose_name_plural = "Calls to Action"

class BlogSEOEssentialInline(nested_admin.NestedStackedInline):
    model = BlogSEOEssential
    extra = 1
    exclude = ("keywords",)
    # form = BlogSEOEssentialForm


class BlogIndustryFilter(admin.SimpleListFilter):
    title = "Industry"
    parameter_name = "industry_details__id__exact"
    def lookups(self, request, model_admin):
        industries = ServeCategory.objects.annotate(total_blog=Count("blogs")).all()
        lookup_list = []
        for industry in list(industries):
            if industry.total_blog == 0:
                lookup_list.append((industry.pk, industry.title))
            else:
                lookup_list.append(
                    (industry.pk, f"{industry.title} ({industry.total_blog})")
                )
        return tuple(lookup_list)
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(industry_details__id__exact=self.value())
        return queryset

class ServiceCategoryFAQInline(nested_admin.NestedTabularInline):
    model = ServiceCategoryFAQ
    extra = 1  # Number of empty FAQ forms to display by default
    fields = ('question', 'answer', 'order')
    ordering = ['order']


class ServeCategoryFAQSchemaInline(nested_admin.NestedStackedInline):
    model = ServeCategoryFAQSchema
    extra = 0  # Don't show empty form
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    


class ServeCategoryCTAInline(nested_admin.NestedStackedInline):
    model = ServeCategoryCTA
    extra = 1
    verbose_name = "Call to Action"
    verbose_name_plural = "Calls to Action"

# ================================= Our Process =================================

class OurProcessInline(nested_admin.NestedStackedInline):
    model = OurProcess
    extra = 1

#================================= CustomSolutions =================================
class CustomSolutionsCardsInline(nested_admin.NestedStackedInline):
    model = CustomSolutionsCards
    extra = 1
    verbose_name = "Benifit Card"
    verbose_name_plural = "Benifit Cards"
    fields = ('card_title', 'card_description')

class CustomSolutionsInline(nested_admin.NestedStackedInline):
    model = CustomSolutions
    extra = 1
    inlines = [CustomSolutionsCardsInline]
    verbose_name = "Benifit"
    verbose_name_plural = "Benifits"

#================================= Benifits =================================
class BenefitsQAInline(nested_admin.NestedStackedInline):
    model = BenefitsQA
    extra = 1
    fields = ('card_title', 'card_description')
    verbose_name = "Benefit QA"
    verbose_name_plural = "Benefit QA's"

class BenefitsInline(nested_admin.NestedStackedInline):
    model = Benefits
    extra = 1
    inlines = [BenefitsQAInline]
    verbose_name = "Benifited Organization"
    verbose_name_plural = "Benifited Organizations"

#================================= Why Choose Us =================================
class WhyChooseUsCardsDetailsInline(nested_admin.NestedStackedInline):
    model = WhyChooseUsCardsDetails
    extra = 1
    verbose_name = "Why Choose Us Card Details"
    verbose_name_plural = "Why Choose Us Card Details"


class WhyChooseUsCardsInline(nested_admin.NestedStackedInline):
    model = WhyChooseUsCards
    extra = 1
    inlines = [WhyChooseUsCardsDetailsInline]
    verbose_name = "Why Choose Us Card"
    verbose_name_plural = "Why Choose Us Cards"

class WhyChooseUsInline(nested_admin.NestedStackedInline):
    model = WhyChooseUs
    extra = 1
    inlines = [WhyChooseUsCardsInline]
    max_num = 1
    min_num = 1

#================================= Industry Details Hero Section =================================

class IndustryDetailsHeroSectionInline(nested_admin.NestedStackedInline):
    model = IndustryDetailsHeroSection
    extra = 1
    max_num = 1
    min_num = 1
    verbose_name = "Hero Section"
    verbose_name_plural = "Hero Sections"

# ================================= IndustryDetailsHeading =================================
class IndustryDetailsHeadingCardsInline(nested_admin.NestedStackedInline):
    model = IndustryDetailsHeadingCards
    extra = 1
    verbose_name = "Solution & Service Card"
    verbose_name_plural = "Solution & Service Cards"
    fields = ('card_title', 'card_description', 'image')


class IndustryDetailsHeadingInline(nested_admin.NestedStackedInline):
    model = IndustryDetailsHeading
    extra = 1
    # max_num = 1
    # min_num = 1  # Ensures at least one instance must exist
    verbose_name = "Software Development Solution & Service"
    verbose_name_plural = "Software Development Solutions & Services"
    inlines = [IndustryDetailsHeadingCardsInline]  # This nests the cards inline
    fields = ('seo_title', 'section_title', 'section_description', 'image')
    # You can add more customization here if needed



class IndustryItemTagsInlineAdmin(nested_admin.NestedStackedInline):
    model = IndustryItemTags
    extra = 1
    min_num = 1
    max_num = 3
# ================================= ServeCategoryAdmin (Industry Details) =================================
@admin.register(ServeCategory)
class ServeCategoryAdmin(nested_admin.NestedModelAdmin):
    search_fields = ['title']
    list_display = ('title', 'slug',)
    inlines = [
               IndustryMetadataInline,
               IndustryDetailsHeroSectionInline,
               IndustryDetailsHeadingInline,
               CustomSolutionsInline, 
               BenefitsInline,
               WhyChooseUsInline,
               OurProcessInline,
               ServiceCategoryFAQInline, 
               ServeCategoryCTAInline, 
               ServeCategoryFAQSchemaInline,
               IndustryItemTagsInlineAdmin
               ]
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('title',)
    change_form_template = 'admin/website/servecategory/change_form.html'

    def save_related(self, request, form, formsets, change):
        # First save all inlines
        super().save_related(request, form, formsets, change)
        
        # Get the main object
        serve_category = form.instance
        
        # Get all FAQs for this serve_category
        faqs = serve_category.faqs.all().order_by('order')
        
        # Delete existing FAQ schema if no FAQs
        ServeCategoryFAQSchema.objects.filter(serve_category=serve_category).delete()
        
        if faqs.exists():
            # Generate FAQ schema
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq.question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq.answer
                        }
                    }
                    for faq in faqs
                ]
            }
            
            # Create new FAQ schema
            ServeCategoryFAQSchema.objects.create(
                serve_category=serve_category,
                faq_schema=mark_safe(
                    '<script type="application/ld+json">\n'
                    f'{json.dumps(faq_schema, indent=2)}\n'
                    '</script>'
                )
            )



# ================================================================Service Page(Services)=============================================================
# @admin.register(ServicePage)
# class ServicePageAdmin(admin.ModelAdmin):
#     search_fields = ['title']
#     prepopulated_fields = {"slug": ("title",)}
#     list_display = ('title', 'slug', 'is_parent')
#     list_filter = ('is_parent',)
class ServicesItemTagsInline(nested_admin.NestedTabularInline):
    model = ServicesItemTags
    extra = 1
# ===========================SolutionsAndServices======================
class SolutionsAndServicesCardsInline(nested_admin.NestedStackedInline):
    model = SolutionsAndServicesCards
    extra = 1
    fields = ('card_title', 'card_description')
    verbose_name = "Solution Card"
    verbose_name_plural = "Solution Cards"
    
class SolutionsAndServicesInline(nested_admin.NestedStackedInline):
    model = SolutionsAndServices
    extra = 1
    inlines = [SolutionsAndServicesCardsInline]

# ===========================Key Things======================
class KeyThingsQAInline(nested_admin.NestedStackedInline):
    model = KeyThingsQA
    extra = 1


class KeyThingsInline(nested_admin.NestedStackedInline):
    model = KeyThings
    extra = 1
    inlines = [KeyThingsQAInline]

# ===========================Best Practices======================

class BestPracticesCardsDetailsInline(nested_admin.NestedStackedInline):
    model = BestPracticesCardsDetails
    extra = 1
    verbose_name = "Best Practices Card Details"
    verbose_name_plural = "Best Practices Card Details"
class BestPracticesCardsInline(nested_admin.NestedStackedInline):
    model = BestPracticesCards
    extra = 1
    inlines = [BestPracticesCardsDetailsInline]
    verbose_name = "Best Practices Card"
    verbose_name_plural = "Best Practices Cards"
class BestPracticesHeadingsInline(nested_admin.NestedStackedInline):
    model = BestPracticesHeadings
    extra = 1
    inlines = [BestPracticesCardsInline]
    max_num = 1
    min_num = 1
    verbose_name = "Best Practices"
    verbose_name_plural = "Best Practices"

# ===========================Why Choose Us======================
class ServicesWhyChooseUsCardsDetailsInline(nested_admin.NestedStackedInline):
    model = ServicesWhyChooseUsCardsDetails
    extra = 1
    verbose_name = "Why Choose Us Card Details"
    verbose_name_plural = "Why Choose Us Card Details"

class ServicesWhyChooseUsCardsInline(nested_admin.NestedStackedInline):
    model = ServicesWhyChooseUsCards
    extra = 1
    inlines = [ServicesWhyChooseUsCardsDetailsInline]
    verbose_name = "Why Choose Us Card"
    verbose_name_plural = "Why Choose Us Cards"

class ServicesWhyChooseUsInline(nested_admin.NestedStackedInline):
    model = ServicesWhyChooseUs
    extra = 1
    inlines = [ServicesWhyChooseUsCardsInline]
    max_num = 1
    min_num = 1
    verbose_name = "Why Choose Us"
    verbose_name_plural = "Why Choose Us"

# ===========================Our Process======================
class ServicesOurProcessInline(nested_admin.NestedStackedInline):
    model = ServicesOurProcess
    extra = 1

# ===========================service page faq and cta======================
class ServicePageCTAInline(nested_admin.NestedStackedInline):
    model = ServicePageCTA
    extra = 1
    verbose_name = "Call to Action"
    verbose_name_plural = "Calls to Action"

class FAQQuestionInline(nested_admin.NestedStackedInline):
    model = ServiceFAQQuestion
    extra = 1

class ServicePageFAQSchemaInline(nested_admin.NestedStackedInline):
    model = ServicePageFAQSchema
    extra = 0
    can_delete = True
    
    def has_add_permission(self, request, obj=None):
        return False

class MetaDescriptionInline(nested_admin.NestedStackedInline):
    model = MetaDescription
    extra = 1
    max_num = 1
    min_num = 1


class ServicesRelatedBlogsInline(nested_admin.NestedStackedInline):
    model = ServicesRelatedBlogs
    extra = 1



@admin.register(ServicePage)
class ServicePageAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        "title",
        "is_parent",
    )
    
    search_fields = ("title",)
    fieldsets = (
        ("Page Hierarchy", {"fields": ("is_parent", "parent", "title", "show_in_menu", "services_body_schema")}),
        (
            "Banner",
            {"fields": ("seo_title", "sub_title", "secondary_title", "slug", "description", "icon", "feature_image")},
        ),
        # ("Explore Our Services", {"fields": ("icon", "feature_image")})
        
        # ("Why Choose Us", {"fields": ("why_choose_us_sub_title",)}),
        # (
        #     "Development Service Process",
        #     {
        #         "fields": (
        #             "development_services_title",
        #             "development_services_sub_title",
        #         )
        #     },
        # ),
        # (
        #     "Comparative Analysis",
        #     {
        #         "fields": (
        #             "comparative_analysis_title",
        #             "comparative_analysis_sub_title",
        #         )
        #     },
        # ),
        # ("FAQ", {"fields": ("faq_short_description",)}),
    )
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        # DiscoverOurServiceInline,
        # AdditionalServiceContentInline,
        # DevelopmentServiceProcessInline,
        # ComparativeAnalysisInline,
        MetaDescriptionInline,
        SolutionsAndServicesInline,
        KeyThingsInline,
        BestPracticesHeadingsInline,
        ServicesWhyChooseUsInline,
        ServicesOurProcessInline,

        FAQQuestionInline,
        ServicePageFAQSchemaInline,
        # ServiceMetaDataInline,
        ServicePageCTAInline,
        ServicesItemTagsInline,
        ServicesRelatedBlogsInline
    ]
    list_per_page = 20
    change_form_template = 'admin/website/servecategory/change_form.html'


    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        
        # Fixed: Changed from technology to service_page
        service_page = form.instance
        
        # Fixed: Changed from faqs to questions
        faqs = service_page.questions.all().order_by('id')  # ServiceFAQQuestion doesn't have an order field
        
        # Fixed: Changed from technology to service_page
        ServicePageFAQSchema.objects.filter(service_page=service_page).delete()
        
        if faqs.exists():
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq.question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq.answer
                        }
                    }
                    for faq in faqs
                ]
            }
            
            # Fixed: Changed from technology to service_page
            ServicePageFAQSchema.objects.create(
                service_page=service_page,
                faq_schema=mark_safe(
                    '<script type="application/ld+json">\n'
                    f'{json.dumps(faq_schema, indent=2)}\n'
                    '</script>'
                )
            )
        
        # Services Body Schema generation (new code)
        try:
            meta_desc = service_page.meta_description
            if meta_desc and (meta_desc.meta_title or meta_desc.meta_description):
                # Get the service page URL
                service_url = request.build_absolute_uri(service_page.get_absolute_url()) if hasattr(service_page, 'get_absolute_url') else f"https://mediusware.com/services/{service_page.slug}"
                
                services_body_schema = {
                    "@context": "https://schema.org",
                    "@graph": [
                        {
                            "@type": "Service",
                            "name": meta_desc.meta_title or service_page.title,
                            "description": meta_desc.meta_description or service_page.description,
                            "provider": "Mediusware LTD",
                            "url": service_url,
                            "termsOfService": "https://mediusware.com/terms"
                        }
                    ]
                }
                
                # Save the schema to the services_body_schema field
                service_page.services_body_schema = mark_safe(
                    '<script type="application/ld+json">\n'
                    f'{json.dumps(services_body_schema, indent=2)}\n'
                    '</script>'
                )
                service_page.save(update_fields=['services_body_schema'])
        except Exception as e:
            # Handle any exceptions, e.g., if meta_description doesn't exist
            print(f"Error generating services body schema: {e}")



# ================================================================ Technology ====================================================================
@admin.register(TechnologyType)
class TechnologyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", )
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("name",)

# @admin.register(TechnologyFAQ)
# class TechnologyFAQAdmin(admin.ModelAdmin):
#     pass

# ==================== Technology FAQ ====================
class TechnologyFAQInline(nested_admin.NestedTabularInline):
    model = TechnologyFAQ
    extra = 1
    fields = ('question', 'answer', 'order')
    ordering = ['order']


class TechnologyFAQSchemaInline(nested_admin.NestedStackedInline):
    model = TechnologyFAQSchema
    extra = 0
    can_delete = True
    
    def has_add_permission(self, request, obj=None):
        return False

# =================== Technology CTA ===================
class TechnologyCTAInline(nested_admin.NestedStackedInline):
    model = TechnologyCTA
    extra = 1
    verbose_name = "Call to Action"
    verbose_name_plural = "Calls to Action"


    
# =============Technology Solution and Services Section================
class TechnologySolutionsAndServicesCardsInline(nested_admin.NestedTabularInline):
    model = TechnologySolutionsAndServicesCards
    extra = 1

class TechnologySolutionsAndServicesInline(nested_admin.NestedStackedInline):
    model = TechnologySolutionsAndServices
    extra = 1
    # inlines = [TechnologySolutionsAndServicesCardsInline]
    max_num = 1
    min_num = 1


class TechnologyCreatorsQuotesInline(nested_admin.NestedTabularInline):
    model = TechnologyCreatorsQuotes
    extra = 1
    verbose_name = "Creator's Quote"
    verbose_name_plural = "Creator's Quotes"

# ===================Technology Services We Provide Section=====================
class ServicesWeProvideCardsInline(nested_admin.NestedTabularInline):
    model = ServicesWeProvideCards
    extra = 1

class ServicesWeProvideInline(nested_admin.NestedStackedInline):
    model = ServicesWeProvide
    extra = 1
    inlines = [ServicesWeProvideCardsInline]
    max_num = 1
    min_num = 1

# ===================Technology EcoSystem Section=====================
class EcoSystemCardTagsInline(nested_admin.NestedTabularInline):
    model = EcoSystemCardTags
    extra = 1

class EcoSystemCardsInline(nested_admin.NestedTabularInline):
    model = EcoSystemCards
    extra = 1
    inlines = [EcoSystemCardTagsInline]

class EcoSystemInline(nested_admin.NestedStackedInline):
    model = EcoSystem
    extra = 1
    inlines = [EcoSystemCardsInline]
    max_num = 1
    min_num = 1

# ===================== Technology Key Things ======================
class TechnologyKeyThingsQAInline(nested_admin.NestedTabularInline):
    model = TechnologyKeyThingsQA
    extra = 1

class TechnologyKeyThingsInline(nested_admin.NestedStackedInline):
    model = TechnologyKeyThings
    extra = 1
    inlines = [TechnologyKeyThingsQAInline]
    max_num = 1
    min_num = 1


# ===========================Why Choose Us======================
class TechnologyWhyChooseUsCardsDetailsInline(nested_admin.NestedStackedInline):
    model = TechnologyWhyChooseUsCardsDetails
    extra = 1
    verbose_name = "Why Choose Us Card Details"
    verbose_name_plural = "Why Choose Us Card Details"

class TechnologyWhyChooseUsCardsInline(nested_admin.NestedStackedInline):
    model = TechnologyWhyChooseUsCards
    extra = 1
    inlines = [TechnologyWhyChooseUsCardsDetailsInline]
    verbose_name = "Why Choose Us Card"
    verbose_name_plural = "Why Choose Us Cards"

class TechnologyWhyChooseUsInline(nested_admin.NestedStackedInline):
    model = TechnologyWhyChooseUs
    extra = 1
    inlines = [TechnologyWhyChooseUsCardsInline]
    max_num = 1
    min_num = 1
    verbose_name = "Why Choose Us"
    verbose_name_plural = "Why Choose Us"

# ================= Our Process of Technology =================
class TechnologyOurProcessInline(nested_admin.NestedStackedInline):
    model=TechnologyOurProcess
    extra=1
    verbose_name="Our Process"
    verbose_name_plural="Our Processes"
    ordering=['order']

# ================= History of Technology =================
class HistoryOfTechInline(nested_admin.NestedStackedInline):
    model = HistoryOfTech
    extra = 1
    min_num = 1
    max_num = 1

class TechnologyMetaDataInline(nested_admin.NestedStackedInline):
    model = TechnologyMetaData
    extra = 1
@admin.register(Technology)
class TechnologyAdmin(nested_admin.NestedModelAdmin):  # Changed to NestedModelAdmin
    list_display = ("name", "slug", "type", "show_in_menu")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    inlines = [
        TechnologyMetaDataInline,
        TechnologySolutionsAndServicesInline,
        TechnologyCreatorsQuotesInline,
        ServicesWeProvideInline,
        EcoSystemInline,
        TechnologyKeyThingsInline,
        TechnologyWhyChooseUsInline,
        TechnologyOurProcessInline,
        HistoryOfTechInline,
        TechnologyFAQInline, 
        TechnologyCTAInline, 
        TechnologyFAQSchemaInline,
    ]
    change_form_template = 'admin/website/servecategory/change_form.html'
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        
        technology = form.instance
        faqs = technology.faqs.all().order_by('order')
        
        TechnologyFAQSchema.objects.filter(technology=technology).delete()
        
        if faqs.exists():
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq.question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq.answer
                        }
                    }
                    for faq in faqs
                ]
            }
            
            TechnologyFAQSchema.objects.create(
                technology=technology,
                faq_schema=mark_safe(
                    '<script type="application/ld+json">\n'
                    f'{json.dumps(faq_schema, indent=2)}\n'
                    '</script>'
                )
            )

# =========================================== Blog Status Filter ===========================================
class BlogStatusFilter(SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        # Get the queryset that the user is allowed to see
        qs = model_admin.get_queryset(request)
        
        # Get counts for each status
        status_counts = qs.values('status').annotate(count=Count('id')).order_by()
        count_dict = {item['status']: item['count'] for item in status_counts}
        
        # Create lookups with counts
        lookups = []
        for status_value, status_label in BlogStatus.choices:
            count = count_dict.get(status_value, 0)
            lookups.append((status_value, f"{status_label} ({count})"))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


@admin.register(Blog)
class BlogAdmin(nested_admin.NestedModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

    inlines = (
        BlogContextInline,
        BlogSEOEssentialInline,
        BlogFAQInline,
        BlogFAQSchemaInline,
        # CTAInline,
        # ReferenceBlogInline,
        # RelatedBlogInline,
        # BlogModeratorFeedbackInline,
        # BlogMetadataInline,
    )
    actions = [
        "clone_selected",
        "draft_selected",
        "in_revision_selected",
        "submit_for_review_selected",
        "approve_selected",
        "plagiarism_check_selected",
    ]

    search_fields = ("title",)
    date_hierarchy = "created_at"
    # autocomplete_fields = ["category", "tag"]
    autocomplete_fields = ["industry_details", "category", "tag", "parent_services", "technology"]  # Updated to industry_details
    list_display = (
        "title",
        "author",
        "status",
        "total_view",
        "get_preview_link",
        # "get_plagiarism_percentage",
    )
    readonly_fields = ("status",)
    exclude = ("content",)

    fields = (
        "title",
        "slug",
        # "status",
        "next_status",
        "image",
        # "video",
        "youtube_link",
        "category",
        "industry_details",  # Updated to industry_details
        # ("parent_services", "child_services"),  # Display side by side
        "parent_services",
        # "technology_type",
        "technology",
        "author",
        # "tag",
        # "short_description",
        "is_featured",
        # "content",
        # "read_time_minute",
        "schema_type", 
        "main_body_schema",
        "hightlighted_text",
        "cta_title",
    )
    form = BlogForm
    list_filter = (BlogStatusFilter, BlogIndustryFilter, ActiveEmployeeFilter)
    list_per_page = 20

    class Media:
        js = ("js/blog_post_field_escape.js", "js/service_filter.js")

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # --- NEW CODE START: Add child_services data for JavaScript ---
        context['child_services'] = ServicePage.objects.filter(is_parent=False).values('id', 'title', 'parent_id')
        # --- NEW CODE END ---
        return context
    
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = BlogForm
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        form.change = obj is not None
        return form

    # @admin.action(description="Deactivate selected blogs")
    # def unapprove_selected(self, request, queryset):
    #     queryset.update(status=)
    #     self.message_user(request, f"Successfully unapproved {queryset.count()} blogs.")

    # list_editable = ("active", "approved",)
    def lookup_allowed(self, lookup, value):
        if lookup in ["created_by__employee__id__exact"]:
            return True
        return super().lookup_allowed(lookup, value)

    @admin.display(description="Created At")
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d %b %Y")

    @admin.display(description="Updated At")
    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%d %b %Y")

    @admin.display(description="Preview")
    def get_preview_link(self, obj):
        url = f"https://www.mediusware.com/blog/{obj.slug}/?q=preview"
        html_template = get_template("blog/col_preview_link.html")
        html_content = html_template.render({"url": url})
        return format_html(html_content)

    @admin.action(description="Change Status To Approved")
    def approve_selected(self, request, queryset):
        queryset.update(status=BlogStatus.APPROVED, approved_at=timezone.now())
        self.message_user(request, f"Successfully approved {queryset.count()} blogs.")

    @admin.action(description="Change Status To Draft")
    def draft_selected(self, request, queryset):
        queryset.update(status=BlogStatus.DRAFT, approved_at=None)
        self.message_user(request, f"Successfully updated {queryset.count()} blogs.")

    @admin.action(description="Change Status To Revision")
    def in_revision_selected(self, request, queryset):
        queryset.update(status=BlogStatus.NEED_REVISION, approved_at=None)
        self.message_user(request, f"Successfully updated {queryset.count()} blogs.")

    @admin.action(description="Change Status To Review")
    def submit_for_review_selected(self, request, queryset):
        queryset.update(status=BlogStatus.SUBMIT_FOR_REVIEW, approved_at=None)
        self.message_user(request, f"Successfully updated {queryset.count()} blogs.")

    @admin.action(description="Submit selected blog(s) for Plagiarism Check")
    def plagiarism_check_selected(self, request, queryset):
        if request.user.has_perm("website.can_add_plagiarism_info"):
            try:
                host_url = request.build_absolute_uri("/")
                check_plagiarism(queryset, host_url)
                self.message_user(
                    request, "Successfully queue blogs for plagiarism check."
                )
            except Exception as e:
                print(e)
                self.message_user(
                    request, f"Failed to queue blogs for plagiarism check: {e}"
                )
        else:
            self.message_user(
                request,
                "You do not have permission to submit blogs for plagiarism check.",
                level="ERROR",
            )


    # @admin.display(description="Plagiarism(%)")
    # def get_plagiarism_percentage(self, obj):
    #     plagiarism_objects = obj.plagiarism_info.order_by("-created_at")
    #     html_template = get_template("blog/plagiarism_report_link.html")
    #     html_content = html_template.render({"plagiarism_objects": plagiarism_objects})
    #     return format_html(html_content)

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
                        "industry_details",  # Updated to industry_details
                        "tag",
                        "parent_services",
                        # "child_services",
                        "technology",
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

                for industry in blog.industry_details.all():  # Updated to industry_details
                    cloned_blog.industry_details.add(industry)

                for tag in blog.tag.all():
                    cloned_blog.tag.add(tag)

                for parent_service in blog.parent_services.all():
                    cloned_blog.parent_services.add(parent_service)
                # for child_service in blog.child_services.all():
                #     cloned_blog.child_services.add(child_service)

                for technology in blog.technology.all():
                    cloned_blog.technology.add(technology)

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

        if not request.user.has_perm("website.can_add_plagiarism_info"):
            # If user does not have permissions to send the blog for plagiarism check
            del actions["plagiarism_check_selected"]

        return actions

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        querySet = super().get_queryset(request)
        user = request.user
        if user.has_perm("website.can_view_all"):
            return querySet
        else:
            return querySet.filter(created_by=user)

    # def get_form(self, request, obj=None, **kwargs):
    #     kwargs['form'] = BlogForm
    #     form = super().get_form(request, obj, **kwargs)
    #     form.request = request
    #     form.change = obj is not None
    #     return form

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
                not (
                    obj.status == BlogStatus.APPROVED
                    or obj.status == BlogStatus.PUBLISHED
                )
                and obj.created_by == request.user
            )
            moderator_permission = not (
                obj.status == BlogStatus.APPROVED or obj.status == BlogStatus.PUBLISHED
            ) and request.user.has_perm("website.can_approve")
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


    # def save_model(self, request, obj, form, change):
    #     # Ensure slug is set
    #     if not obj.slug:
    #         from django.utils.text import slugify
    #         obj.slug = slugify(obj.title)[:50]

    #     # # Save the object first to ensure inlines are processed
    #     # super().save_model(request, obj, form, change)

    #     # Get the first BlogSEOEssential object, if it exists
    #     seo_essential = obj.blogseoessential_set.first()  # Use default reverse relation
    #     seo_description = seo_essential.description if seo_essential else ""

    #     # Generate JSON-LD schema
    #     schema_data = {
    #         "@context": "https://schema.org",
    #         "@type": obj.schema_type,
    #         "mainEntityOfPage": {
    #             "@type": "WebPage",
    #             "@id": f"https://www.mediusware.com/blog/{obj.slug}/"
    #         },
    #         "headline": obj.title,
    #         "description": seo_description,
    #         "image": obj.image.url if obj.image else "",
    #         "author": {
    #             "@type": "",
    #             "name": f"{obj.created_by.first_name} {obj.created_by.last_name}" if obj.created_by else ""
    #         },
    #         "publisher": {
    #             "@type": "Organization",
    #             "name": "",
    #             "logo": {
    #                 "@type": "ImageObject",
    #                 "url": ""
    #             }
    #         },
    #         "datePublished": obj.approved_at.isoformat() if obj.approved_at else obj.created_at.isoformat()  # Use created_at as fallback
    #     }

    #     # Wrap the JSON in <script> tags
    #     schema_html = mark_safe(
    #         '<script type="application/ld+json">\n'
    #         f'{json.dumps(schema_data, indent=2)}\n'
    #         '</script>'
    #     )

    #     # Assign the schema to main_body_schema
    #     obj.main_body_schema = schema_html

    #     # Save the object
    #     super().save_model(request, obj, form, change)

    #     # Handle approval logic
    #     if obj.status == BlogStatus.APPROVED and (request.user.is_superuser or request.user.has_perm("website.can_approve")):
    #         obj.approved_at = timezone.now()
    #     else:
    #         obj.approved_at = None
    #     obj.save()


    # def save_related(self, request, form, formsets, change):
    #     super().save_related(request, form, formsets, change)
    #     blog = form.instance
    #     faqs = blog.blog_faqs.all()
    #     # Delete existing BlogFAQSchema if no FAQs
    #     BlogFAQSchema.objects.filter(blog=blog).delete()
    #     if faqs.exists():
    #         faq_schema = {
    #             "@context": "https://schema.org",
    #             "@type": "FAQPage",
    #             "mainEntity": [
    #                 {
    #                     "@type": "Question",
    #                     "name": faq.question or "",
    #                     "acceptedAnswer": {
    #                         "@type": "Answer",
    #                         "text": faq.answer or ""
    #                     }
    #                 }
    #                 for faq in faqs
    #             ]
    #         }
    #         BlogFAQSchema.objects.create(
    #             blog=blog,
    #             faq_schema=mark_safe(
    #                 '<script type="application/ld+json">\n'
    #                 f'{json.dumps(faq_schema, indent=2)}\n'
    #                 '</script>'
    #             )
    #         )


    def save_model(self, request, obj, form, change):
        # Ensure slug is set
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.title)[:50]
        
        # Save the object first
        super().save_model(request, obj, form, change)
        
        # Handle approval logic
        if obj.status == BlogStatus.APPROVED and (request.user.is_superuser or request.user.has_perm("website.can_approve")):
            obj.approved_at = timezone.now()
        else:
            obj.approved_at = None
        obj.save()

    def save_related(self, request, form, formsets, change):
        # First save all inlines
        super().save_related(request, form, formsets, change)
        
        # Now get the main object
        obj = form.instance
        
        # Get the first BlogSEOEssential object after inlines are saved
        seo_essential = obj.blogseoessential_set.first()
        seo_description = seo_essential.description if seo_essential else ""
        
        # Generate JSON-LD schema
        schema_data = {
            "@context": "https://schema.org",
            "@type": obj.schema_type,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"https://www.mediusware.com/blog/{obj.slug}/"
            },
            "headline": obj.title,
            "description": seo_description,
            "image": obj.image.url if obj.image else "",
            "author": {
                "@type": "Person",
                # "name": f"{obj.created_by.first_name} {obj.created_by.last_name}" if obj.created_by else ""
                "name": f"{obj.author}" if obj.author else ""

            },
            "publisher": {
                "@type": "Organization",
                "name": "Mediusware LTD.",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://mediusware.com/brand.svg"
                }
            },
            "datePublished": obj.approved_at.isoformat() if obj.approved_at else obj.created_at.isoformat()
        }
        
        # Wrap the JSON in <script> tags
        schema_html = mark_safe(
            '<script type="application/ld+json">\n'
            f'{json.dumps(schema_data, indent=2)}\n'
            '</script>'
        )
        
        # Assign the schema to main_body_schema
        obj.main_body_schema = schema_html
        
        # Save the main model again to update the schema
        obj.save()

        # Handle FAQ schema (existing code)
        faqs = obj.blog_faqs.all()
        # Delete existing BlogFAQSchema if no FAQs
        BlogFAQSchema.objects.filter(blog=obj).delete()
        if faqs.exists():
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq.question or "",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq.answer or ""
                        }
                    }
                    for faq in faqs
                ]
            }
            BlogFAQSchema.objects.create(
                blog=obj,
                faq_schema=mark_safe(
                    '<script type="application/ld+json">\n'
                    f'{json.dumps(faq_schema, indent=2)}\n'
                    '</script>'
                )
            )

    


# @admin.register(BlogComment)
# class BlogCommentModelAdmin(MPTTModelAdmin):
#     mptt_level_indent = 20
#     list_display = ["id", "name"]



# ================================================ Additional Page Admin ================================================================
class AdditionalPageHeroSectionInline(nested_admin.NestedStackedInline):
    model = AdditionalPageHeroSection
    extra = 1
    max_num = 1
    min_num = 1
    verbose_name = "Hero Section"
    verbose_name_plural = "Hero Section"


class WhatIsInline(nested_admin.NestedStackedInline):
    model = WhatIs
    extra = 1
    max_num = 1
    min_num = 1
    verbose_name = "What Is"
    verbose_name_plural = "What Is"


class AdditionalPageKeyThingsCardsInline(nested_admin.NestedStackedInline):
    model = AdditionalPageKeyThingsCards
    extra = 1
    verbose_name = "Key Things Card"
    verbose_name_plural = "Key Things Cards"

class AdditionalPageKeyThingsInline(nested_admin.NestedStackedInline):
    model = AdditionalPageKeyThings
    extra = 1
    inlines = [AdditionalPageKeyThingsCardsInline]
    max_num = 1
    min_num = 1
    verbose_name = "Key Things"
    verbose_name_plural = "Key Things"

class AdditionalPageWhyChooseUsInline(nested_admin.NestedStackedInline):
    model = AdditionalPageWhyChooseUs
    extra = 1
    verbose_name = "Why Choose Us"
    verbose_name_plural = "Why Choose Us"
    max_num = 1
    min_num = 1

class AdditionalPageOurProcessInline(nested_admin.NestedStackedInline):
    model = AdditionalPageOurProcess
    extra = 1
    verbose_name = "Our Process"
    verbose_name_plural = "Our Processes"

class AdditionalPageFAQInline(nested_admin.NestedStackedInline):
    model = AdditionalPageFAQ
    extra = 1
    verbose_name = "FAQ"
    verbose_name_plural = "FAQ's"

class TeamElementInline(nested_admin.NestedStackedInline):
    model = TeamElement
    extra = 1


@admin.register(AdditionalPages)
class AdditionalPagesAdmin(nested_admin.NestedModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ["title", "slug"]
    inlines = [
        AdditionalPageHeroSectionInline,
        WhatIsInline,
        AdditionalPageKeyThingsInline,
        AdditionalPageWhyChooseUsInline,
        AdditionalPageOurProcessInline,
        AdditionalPageFAQInline,
        TeamElementInline

        
    ]

# ===================================================== Awards Admin ============================================================

class AwardsInline(nested_admin.NestedStackedInline):
    model = Awards
    extra = 1
    verbose_name = "Award"
    verbose_name_plural = "Awards"

class AwardYearGroupInline(nested_admin.NestedStackedInline):
    model = AwardYearGroup
    extra = 1
    inlines = [AwardsInline]

@admin.register(AwardCategory)
class AwardCategoryAdmin(nested_admin.NestedModelAdmin):
    list_display = ('id', 'section_title', 'section_description')
    search_fields = ('section_title',)
    inlines = [AwardYearGroupInline]



@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    model = FAQ
    list_display = ["question", "answer"]

    def has_module_permission(self, request):
        return False


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


# @admin.register(EmployeePerspective)
# class EmployeePerspectiveAdmin(admin.ModelAdmin):
#     list_display = (
#         "employee",
#         "title",
#         "description",
#     )


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


# @admin.register(Lead)
# class LeadAdmin(admin.ModelAdmin):
#     list_display = ("name", "email", "message")
#     search_fields = ("name", "email")
#     list_filter = ("name", "email")
#     ordering = ("name",)
#     fields = ("name", "email", "message")
#     # date_hierarchy = "created_at"


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

    def has_module_permission(self, request):
        return False


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


class EmployeeTestimonialTitleInline(admin.StackedInline):
    model = EmployeeTestimonialTitle
    can_delete = False
    extra = 1


class BenefitsOfEmploymentTitleInline(admin.StackedInline):
    model = BenefitsOfEmploymentTitle
    can_delete = False
    extra = 1


# Register the WebsiteTitle admin with all the inlines
@admin.register(WebsiteTitle)
class WebsiteTitleAdmin(admin.ModelAdmin):
    list_display = ("title",)
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
        EmployeeTestimonialTitleInline,
        BenefitsOfEmploymentTitleInline,
    ]

    def has_module_permission(self, request):
        return False


class BaseInline(admin.StackedInline):
    can_delete = False
    extra = 1


class LeaderShipBannerInline(BaseInline):
    model = LeaderShipBanner
    verbose_name = "Leadership Banner"


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


class CareerBannerInline(BaseInline):
    model = CareerBanner
    verbose_name = "Career Banner"


@admin.register(PageBanner)
class PageBannerAdmin(admin.ModelAdmin):
    list_display = ("title",)
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
        LeaderShipBannerInline,
        CareerBannerInline,
    ]
    def has_module_permission(self, request):
        return False


class LeadershipSpeechInline(admin.StackedInline):
    model = LeadershipSpeech
    extra = 1
    autocomplete_fields = ("leader",)
    search_fields = ("leader__full_name",)
    # fields = ("leader", "video_url", "thumbnail", "description", "speech")


@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display = ("title",)
    inlines = [LeadershipSpeechInline]
    search_fields = ("leader__full_name",)


@admin.register(EventCalender)
class EventCalenderAdmin(admin.ModelAdmin):
    list_display = ("title", "publish_date")
    search_fields = ("title",)
    date_hierarchy = "publish_date"
    fields = ("title", "description", "image", "publish_date")

    def has_module_permission(self, request):
        return False


class EmployeeTestimonialInline(admin.StackedInline):
    model = EmployeeTestimonial
    extra = 1
    autocomplete_fields = ("employee",)


class BenefitsOfEmploymentInline(admin.StackedInline):
    model = BenefitsOfEmployment
    extra = 1


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    inlines = [EmployeeTestimonialInline, BenefitsOfEmploymentInline]

    def has_module_permission(self, request):
        return False


@admin.register(PublicImage)
class PublicImageAdmin(admin.ModelAdmin):
    list_display = ["title", "image"]


# @admin.register(PlagiarismInfo)
# class PlagiarismInfoAdmin(admin.ModelAdmin):
#     list_display = ["blog", "plagiarism_percentage", "scan_id", "export_id", "pdf_file"]


# @admin.register(ContactForm)
# class ContactFormAdmin(admin.ModelAdmin):
#     list_display = ("full_name", "email", "form_type", "client_query", "project_details", "created_at")
#     # readonly_fields = ["full_name", "email", "form_type", "service_require", "project_details", "client_query", "attached_file", "created_at"]



# @admin.register(ContactForm)
# class ContactFormAdmin(admin.ModelAdmin):
#     list_display = (
#         "full_name",
#         "email",
#         "form_type",
#         "client_query_truncated",
#         "project_details_truncated",
#         "created_at"
#     )

#     # Optional: Make fields read-only if needed
#     # readonly_fields = [...]  # keep your existing if needed

#     def client_query_truncated(self, obj):
#         if not obj.client_query:
#             return "-"
#         truncated = Truncator(obj.client_query).words(5, html=True)  # or .chars(50)
#         return format_html(
#             '<span title="{}">{}</span>',
#             obj.client_query,
#             truncated
#         )
#     client_query_truncated.short_description = "Client Query"
#     client_query_truncated.admin_order_field = "client_query"

#     def project_details_truncated(self, obj):
#         if not obj.project_details:
#             return "-"
#         truncated = Truncator(obj.project_details).words(5, html=True)
#         return format_html(
#             '<span title="{}">{}</span>',
#             obj.project_details,
#             truncated
#         )
#     project_details_truncated.short_description = "Project Details"
#     project_details_truncated.admin_order_field = "project_details"




# ===================== modal=====================
# @admin.register(ContactForm)
# class ContactFormAdmin(admin.ModelAdmin):
#     list_display = (
#         "full_name",
#         "email",
#         "form_type",
#         "client_query_truncated",
#         "project_details_truncated",
#         "created_at"
#     )

#     def client_query_truncated(self, obj):
#         if not obj.client_query:
#             return "-"
#         truncated = Truncator(obj.client_query).words(5, html=True)
#         return format_html(
#             '<a href="#" class="popup-link" data-content="{}" data-title="Client Query">{}</a>',
#             obj.client_query,
#             truncated
#         )
#     client_query_truncated.short_description = "Client Query"
#     client_query_truncated.admin_order_field = "client_query"

#     def project_details_truncated(self, obj):
#         if not obj.project_details:
#             return "-"
#         truncated = Truncator(obj.project_details).words(5, html=True)
#         return format_html(
#             '<a href="#" class="popup-link" data-content="{}" data-title="Project Details">{}</a>',
#             obj.project_details,
#             truncated
#         )
#     project_details_truncated.short_description = "Project Details"
#     project_details_truncated.admin_order_field = "project_details"

#     class Media:
#         css = {
#             'all': ('css/admin_popup.css',)
#         }
#         js = ('js/admin_popup.js',)

@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "form_type",
        # "client_query_truncated",
        # "project_details_truncated",
        "short_brief_truncated",
        "created_at"
    )

    def short_brief_truncated(self, obj):
        if not obj.short_brief:
            return "-"
        truncated = Truncator(obj.short_brief).words(5, html=True)
        return format_html(
            '<span class="tooltip" data-tooltip="{}">{}</span>',
            obj.short_brief,
            truncated
        )
    short_brief_truncated.short_description = "Short Brief"
    short_brief_truncated.admin_order_field = "short_brief"

    # def project_details_truncated(self, obj):
    #     if not obj.project_details:
    #         return "-"
    #     truncated = Truncator(obj.project_details).words(5, html=True)
    #     return format_html(
    #         '<span class="tooltip" data-tooltip="{}">{}</span>',
    #         obj.project_details,
    #         truncated
    #     )
    # project_details_truncated.short_description = "Project Details"
    # project_details_truncated.admin_order_field = "project_details"

    class Media:
        css = {
            'all': ('css/admin_popup.css',)
        }








@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("title", )

@admin.register(ArchivePage)
class ArchivePageAdmin(admin.ModelAdmin):
    list_display = ("seo_title", "slug", "section_title", "section_description")