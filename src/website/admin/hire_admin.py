from django import forms
from django.contrib import admin
from django.http import HttpRequest
import nested_admin

from website.admin.hire_inline_admin import (
    FAQContentInlineAdmin,
    HireResourceFeatureContentInlineAdmin,
    HireTechnologyInlineAdmin,
    whyWeAreInlineAdmin,
)
from website.hire_models import (
    HireEngagement,
    HireEngagementContent,
    HirePricing,
    HireResource,
    HireResourceContent,
    HireResourceFAQ,
    HireResourceFeature,
    HireResourceStatistic,
    HireResourceStatisticContent,
    HireService,
    HireServiceContent,
    HiringProcess,
    HiringProcessContent,
    OnDemandTeam,
    Pricing,
    Quote,
    WhyWeAreContent,
    WorldClassTalent,
)
from website.models import HireResourceKeyword, HireResourceMetadata
from website.models_v2.hire_resources import (
    BenifitCards,
    Benifits,
    ComprehensiveGuide,
    ComprehensiveGuideSectionQnA,
    ComprehensiveGuideSections,
    DefiningDeveloperCards,
    DefiningDevelopers,
    DeliveryModuleIntro,
    FAQQuestion,
    HireDeveloperFAQ,
    HireDeveloperMetaDescription,
    HireDeveloperPage,
    HireDevelopersOurProcess,
    HireResourcePage,
    HireResourceService,
    HireResourceServiceContent,
    HiringComparison,
    HiringFreeLancer,
    HiringStep,
    Cost,
    CostType,
    Criteria,
    DeveloperPriceType,
    HiringThroughMediusware,
    Qualities,
    QualityCards,
    WorkingMechanism,
)


@admin.register(CostType)
class CostTypeAdmin(admin.ModelAdmin):
    def has_module_permission(self, request: HttpRequest) -> bool:
        return False


class CostAdmin(nested_admin.NestedTabularInline):
    model = Cost
    extra = 1


class HiringStepAdmin(nested_admin.NestedTabularInline):
    model = HiringStep
    extra = 1


@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    def has_module_permission(self, request: HttpRequest) -> bool:
        return False


class DeveloperPriceTypeAdmin(nested_admin.NestedTabularInline):
    model = DeveloperPriceType
    extra = 1


class FAQQuestionInlineAdmin(nested_admin.NestedTabularInline):
    model = FAQQuestion
    extra = 1


class HireResourceServiceAdmin(nested_admin.NestedStackedInline):
    model = HireResourceService
    extra = 1


class HireResourceKeywordInline(nested_admin.NestedTabularInline):
    model = HireResourceKeyword
    extra = 1

class HireResourceMetadataInline(nested_admin.NestedStackedInline):
    model = HireResourceMetadata
    extra = 1
    inlines = [HireResourceKeywordInline]

class HireResourceServiceContentInline(nested_admin.NestedStackedInline):
    model = HireResourceServiceContent
    extra = 1



@admin.register(HireResourcePage)
class HireResourcePageAdmin(nested_admin.NestedModelAdmin):
    inlines = [
        CostAdmin,
        DeveloperPriceTypeAdmin,
        HiringStepAdmin,
        HireResourceServiceAdmin,
        FAQQuestionInlineAdmin,
        HireResourceMetadataInline,
        HireResourceServiceContentInline
    ]
    fieldsets = (
        ("Page Hierarchy", {"fields": ("is_parent", "parents")}),
        ("Banner", {"fields": ("title", "sub_title", "image", "slug")}),
        ("Overview", {"fields": ("overview_title", "overview_description")}),
        (
            "Approx Cost",
            {
                "fields": (
                    "pricing_title",
                    "pricing_sub_title",
                )
            },
        ),
        (
            "Developer Pricing",
            {
                "fields": (
                    "developer_pricing_title",
                    "developer_pricing_sub_title",
                )
            },
        ),
        (
            "Hiring Process",
            {
                "fields": (
                    "hiring_process_title",
                    "hiring_process_sub_title",
                )
            },
        ),
        (
            "FAQ",
            {"fields": ("faq_sub_title",)},
        ),
    )
    prepopulated_fields = {"slug": ("title",)}

    def has_module_permission(self, request: HttpRequest) -> bool:
        return False


class HireResourceForm(forms.ModelForm):
    title = forms.CharField(
        max_length=255,
        help_text="if tag exist and set it then title will be not mandatory",
        required=False,
    )

    class Meta:
        model = HireResource
        fields = "__all__"


class HireResourceAdminMixin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"

    def has_module_permission(self, request: HttpRequest) -> bool:
        return False


@admin.register(HireServiceContent)
class HireServiceContentAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")


@admin.register(HireResourceStatisticContent)
class HireResourceStatisticContentAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")


@admin.register(HiringProcess)
class HiringProcessAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")


@admin.register(HiringProcessContent)
class HiringProcessContentAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description", "icon")
    search_fields = ("title", "sub_title", "description")


@admin.register(WhyWeAreContent)
class WhyWeAreContentAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")


@admin.register(HireResourceFeature)
class HireResourceFeatureAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")
    inlines = [HireResourceFeatureContentInlineAdmin]


@admin.register(HireResourceStatistic)
class HireResourceStatisticAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")


@admin.register(HireService)
class HireServiceAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")


@admin.register(Quote)
class QuoteAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")


@admin.register(HireResource)
class HireResourceAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "tag", "description")
    search_fields = ("title", "sub_title", "tag", "description")
    form = HireResourceForm


@admin.register(WorldClassTalent)
class WorldClassTalentAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")


@admin.register(OnDemandTeam)
class OnDemandTeamInAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")


# @admin.register(HireResourceContent)
# class HireResourceContentAdmin(HireResourceAdminMixin):
#     inlines = [
#         HireTechnologyInlineAdmin,
#         whyWeAreInlineAdmin,
#     ]
#     list_display = (
#         "resource",
#         "tag",
#         "title",
#         "sub_title",
#         "description",
#     )
#     search_fields = ("title", "sub_title", "tag", "description")
#     fields = (
#         "resource",
#         "service",
#         "pricing",
#         "statistic",
#         "feature",
#         "hire_process",
#         "engagement",
#         "faq",
#         "tag",
#         "title",
#         "slug",
#         "sub_title",
#         "description",
#         "awards",
#         "world_class_talent",
#         "on_demand_team",
#         "quote",
#     )
#     form = HireResourceForm

#     def has_module_permission(self, request: HttpRequest) -> bool:
#         return True


@admin.register(HireEngagement)
class HireEngagementAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")


@admin.register(HireEngagementContent)
class HireEngagementContentAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")


@admin.register(HireResourceFAQ)
class HireResourceFAQAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")
    inlines = [FAQContentInlineAdmin]


@admin.register(Pricing)
class PricingAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")


@admin.register(HirePricing)
class HirePricingAdmin(HireResourceAdminMixin):
    list_display = ("title", "sub_title", "description")
    search_fields = ("title", "sub_title", "description")


# =====================================================================================================================

class DeliveryModuleIntroInline(nested_admin.NestedStackedInline):
    model = DeliveryModuleIntro
    extra = 0

class WorkingMechanismInline(nested_admin.NestedStackedInline):
    model = WorkingMechanism
    extra = 0

class BenifitCardsInline(nested_admin.NestedTabularInline):
    model = BenifitCards
    extra = 0

class BenifitsInline(nested_admin.NestedStackedInline):
    model = Benifits
    extra = 0
    inlines = [BenifitCardsInline]

class HireDevelopersOurProcessInline(nested_admin.NestedStackedInline):
    model = HireDevelopersOurProcess
    extra = 0
    sortable_field_name = "order"


class HiringThroughMediuswareInline(nested_admin.NestedTabularInline):
    model = HiringThroughMediusware
    extra = 0


class HiringFreelanceInline(nested_admin.NestedTabularInline):
    model = HiringFreeLancer
    extra = 0

class HiringComparisonInline(nested_admin.NestedStackedInline):
    model = HiringComparison
    extra = 0
    inlines = [HiringThroughMediuswareInline, HiringFreelanceInline]
    max_num = 1

class ComprehensiveGuideSectionQnAInline(nested_admin.NestedTabularInline):
    model = ComprehensiveGuideSectionQnA
    extra = 0

class ComprehensiveGuideSectionsInline(nested_admin.NestedStackedInline):
    model = ComprehensiveGuideSections
    extra = 0
    inlines = [ComprehensiveGuideSectionQnAInline]

class ComprehensiveGuideInline(nested_admin.NestedStackedInline):
    model = ComprehensiveGuide
    extra = 0
    inlines = [ComprehensiveGuideSectionsInline]


class DefiningDeveloperCardsInline(nested_admin.NestedTabularInline):
    model = DefiningDeveloperCards
    extra = 0

class DefiningDevelopersInline(nested_admin.NestedStackedInline):
    model = DefiningDevelopers
    extra = 0
    inlines = [DefiningDeveloperCardsInline]

class QualityCardsInline(nested_admin.NestedTabularInline):
    model = QualityCards
    extra = 0

class QualitiesInline(nested_admin.NestedStackedInline):
    model = Qualities
    extra = 0
    inlines = [QualityCardsInline]

class HireDeveloperFAQInline(nested_admin.NestedTabularInline):
    model = HireDeveloperFAQ
    extra = 0

class HireDeveloperMetaDescriptionInline(nested_admin.NestedStackedInline):
    model = HireDeveloperMetaDescription
    extra = 0
    max_num = 1


@admin.register(HireDeveloperPage)
class HireDeveloperPageAdmin(nested_admin.NestedModelAdmin):
    list_display = ("seo_title", "section_title", "secondary_title")
    search_fields = ("seo_title", "section_title", "secondary_title")
    inlines = (
        DeliveryModuleIntroInline,
        WorkingMechanismInline,
        BenifitsInline,
        HireDevelopersOurProcessInline,
        HiringComparisonInline,
        ComprehensiveGuideInline,
        DefiningDevelopersInline,
        QualitiesInline,
        HireDeveloperFAQInline,
        HireDeveloperMetaDescriptionInline,
    )



    