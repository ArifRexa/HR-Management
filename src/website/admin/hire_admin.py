from django import forms
from django.contrib import admin
from django.http import HttpRequest

from website.admin.hire_inline_admin import (
    FAQContentInlineAdmin,
    HireResourceFeatureContentInlineAdmin,
    HireTechnologyInlineAdmin,
    PricingInlineAdmin,
    whyWeAreInlineAdmin,
)
from website.hire_models import (
    HireEngagement,
    HireEngagementContent,
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
    Quote,
    WhyWeAreContent,
    WorldClassTalent,
)


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


@admin.register(HireResourceContent)
class HireResourceContentAdmin(HireResourceAdminMixin):
    inlines = [
        PricingInlineAdmin,
        HireTechnologyInlineAdmin,
        whyWeAreInlineAdmin,
    ]
    list_display = (
        "resource",
        "tag",
        "title",
        "sub_title",
        "description",
    )
    search_fields = ("title", "sub_title", "tag", "description")
    fields = (
        "resource",
        "service",
        "statistic",
        "feature",
        "hire_process",
        "engagement",
        "faq",
        "tag",
        "title",
        "slug",
        "sub_title",
        "description",
        "awards",
        "world_class_talent",
        "on_demand_team",
        "quote",
    )
    form = HireResourceForm

    def has_module_permission(self, request: HttpRequest) -> bool:
        return True


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
