from django.contrib import admin

from website.models_v2.services import (
    ComparativeAnalysis,
    DevelopmentServiceProcess,
    DiscoverOurService,
    ServiceCriteria,
    ServiceFAQQuestion,
    ServicePage,
)


class DiscoverOurServiceInline(admin.StackedInline):
    model = DiscoverOurService
    extra = 1


class DevelopmentServiceProcessInline(admin.TabularInline):
    model = DevelopmentServiceProcess
    extra = 1


class ComparativeAnalysisInline(admin.TabularInline):
    model = ComparativeAnalysis
    extra = 1


class FAQQuestionInline(admin.TabularInline):
    model = ServiceFAQQuestion
    extra = 1


@admin.register(ServiceCriteria)
class ServiceCriteriaAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)


@admin.register(ServicePage)
class ServicePageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_parent",
    )
    search_fields = ("title",)
    fieldsets = (
        ("Page Hierarchy", {"fields": ("is_parent", "parent")}),
        ("Banner", {"fields": ("title", "sub_title", "banner_query", "slug")}),
        (
            "Development Service Process",
            {
                "fields": (
                    "development_services_title",
                    "development_services_sub_title",
                )
            },
        ),
        (
            "Comparative Analysis",
            {
                "fields": (
                    "comparative_analysis_title",
                    "comparative_analysis_sub_title",
                )
            },
        ),
        ("FAQ", {"fields": ("faq_short_description",)}),
    )
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        DiscoverOurServiceInline,
        DevelopmentServiceProcessInline,
        ComparativeAnalysisInline,
        FAQQuestionInline,
    ]
