from django.contrib import admin

from website.models_v2.services import (
    AdditionalServiceContent,
    ComparativeAnalysis,
    DevelopmentServiceProcess,
    DiscoverOurService,
    ServiceCriteria,
    ServiceFAQQuestion,
    ServiceMetaData,
    ServicePage,
)


class ServiceMetaDataInline(admin.StackedInline):
    model = ServiceMetaData
    extra = 1


class DiscoverOurServiceInline(admin.StackedInline):
    model = DiscoverOurService
    extra = 1


class DevelopmentServiceProcessInline(admin.TabularInline):
    model = DevelopmentServiceProcess
    extra = 1


class AdditionalServiceContentInline(admin.StackedInline):
    model = AdditionalServiceContent
    extra = 1


class ComparativeAnalysisInline(admin.TabularInline):
    model = ComparativeAnalysis
    extra = 1


# class FAQQuestionInline(admin.TabularInline):
#     model = ServiceFAQQuestion
#     extra = 1


# @admin.register(ServiceCriteria)
# class ServiceCriteriaAdmin(admin.ModelAdmin):
#     list_display = ("title",)
#     search_fields = ("title",)



# @admin.register(ServicePage)
# class ServicePageAdmin(admin.ModelAdmin):
#     list_display = (
#         "title",
#         "is_parent",
#     )
#     search_fields = ("title",)
#     fieldsets = (
#         ("Page Hierarchy", {"fields": ("is_parent", "parent")}),
#         (
#             "Banner",
#             {"fields": ("title", "sub_title", "banner_query", "slug", "description")},
#         ),
#         ("Explore Our Services", {"fields": ("icon", "feature_image")}),
#         ("Menu", {"fields": ("menu_title",)}),
#         ("Why Choose Us", {"fields": ("why_choose_us_sub_title",)}),
#         (
#             "Development Service Process",
#             {
#                 "fields": (
#                     "development_services_title",
#                     "development_services_sub_title",
#                 )
#             },
#         ),
#         (
#             "Comparative Analysis",
#             {
#                 "fields": (
#                     "comparative_analysis_title",
#                     "comparative_analysis_sub_title",
#                 )
#             },
#         ),
#         ("FAQ", {"fields": ("faq_short_description",)}),
#     )
#     prepopulated_fields = {"slug": ("title",)}
#     inlines = [
#         DiscoverOurServiceInline,
#         AdditionalServiceContentInline,
#         DevelopmentServiceProcessInline,
#         ComparativeAnalysisInline,
#         FAQQuestionInline,
#         ServiceMetaDataInline,
#     ]
#     list_per_page = 20
