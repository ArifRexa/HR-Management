from django.contrib import admin

from website.hire_models import (
    HireResourceFeatureContent,
    HireResourceTechnology,
    Pricing,
    WhyWeAre,
    FAQContent,
)


class FAQContentInlineAdmin(admin.TabularInline):
    model = FAQContent
    fields = ("question", "answer")
    extra = 1

# class PricingInlineAdmin(admin.TabularInline):
#     model = Pricing
#     fields = ("title", "sub_title", "price", "description", "is_active")
#     extra = 1


class HireTechnologyInlineAdmin(admin.TabularInline):
    model = HireResourceTechnology
    fields = ("title", "technologies")
    extra = 1


class whyWeAreInlineAdmin(admin.TabularInline):
    model = WhyWeAre
    fields = ("title", "sub_title", "description", "content")
    extra = 1




class HireResourceFeatureContentInlineAdmin(admin.TabularInline):
    model = HireResourceFeatureContent
    fields = ("title", "description")