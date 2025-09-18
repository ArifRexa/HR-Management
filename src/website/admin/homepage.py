import nested_admin
from django.contrib import admin

from website.models import (
    AwardsHomePage,
    BeginningOfWorking,
    BlogsAndArticlesHomePage,
    CaseStudyHomePage,
    HomePage,
    HomePageHeroAnimatedTitle,
    IndustryWeServeHomePage,
    OurProcessHome,
    TechStack,
    TestimonialsHomePage,
)


class HomePageHeroAnimatedTitleInline(nested_admin.NestedStackedInline):
    model = HomePageHeroAnimatedTitle
    extra = 1


class BeginningOfWorkingInline(nested_admin.NestedStackedInline):
    model = BeginningOfWorking
    extra = 0
    fields = ("seo_title", "section_title", "secondary_title", "section_description")
    verbose_name = "Beginning of Working"
    verbose_name_plural = "Beginning of Working"


class IndustryWeServeHomePageInline(nested_admin.NestedStackedInline):
    model = IndustryWeServeHomePage
    extra = 0
    fields = ("seo_title", "section_title", "secondary_title", "section_description")
    verbose_name = "Industry We Serve"
    verbose_name_plural = "Industries We Serve"


class TechStackInline(nested_admin.NestedStackedInline):
    model = TechStack
    extra = 0
    fields = ("seo_title", "section_title", "secondary_title", "section_description")
    verbose_name = "Tech Stack"
    verbose_name_plural = "Tech Stacks"


class TestimonialsHomePageInline(nested_admin.NestedStackedInline):
    model = TestimonialsHomePage
    extra = 0
    fields = ("seo_title", "section_title", "secondary_title", "section_description")
    verbose_name = "Testimonial Section"
    verbose_name_plural = "Testimonial Sections"


class AwardsHomePageInline(nested_admin.NestedStackedInline):
    model = AwardsHomePage
    extra = 0
    fields = ("seo_title", "section_title", "secondary_title", "section_description")
    verbose_name = "Award Section"
    verbose_name_plural = "Award Sections"


class BlogsAndArticlesHomePageInline(nested_admin.NestedStackedInline):
    model = BlogsAndArticlesHomePage
    extra = 0
    fields = ("seo_title", "section_title", "secondary_title", "section_description")
    verbose_name = "Blog & Article Section"
    verbose_name_plural = "Blog & Article Sections"


class CaseStudyHomePageInline(nested_admin.NestedStackedInline):
    model = CaseStudyHomePage
    extra = 0
    fields = ("seo_title", "section_title", "secondary_title", "section_description")
    verbose_name = "Case Study Section"
    verbose_name_plural = "Case Study Sections"


class OurProcessHomeInline(nested_admin.NestedStackedInline):
    model = OurProcessHome
    extra = 1

@admin.register(HomePage)
class HomePageAdmin(nested_admin.NestedModelAdmin):
    model = HomePage
    inlines = [
        HomePageHeroAnimatedTitleInline,
        BeginningOfWorkingInline,
        IndustryWeServeHomePageInline,
        TechStackInline,
        TestimonialsHomePageInline,
        AwardsHomePageInline,
        BlogsAndArticlesHomePageInline,
        CaseStudyHomePageInline,
        OurProcessHomeInline
    ]
