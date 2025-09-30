from django.db import models
from tinymce.models import HTMLField


class CostType(models.Model):
    cost_type = models.CharField(max_length=255)

    def __str__(self):
        return self.cost_type





class Criteria(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class HireResourcePage(models.Model):
    is_parent = models.BooleanField(default=False)
    parents = models.ForeignKey(
        "self",
        related_name="children",
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"is_parent": True},
        blank=True,
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    image = models.ImageField(
        upload_to="hire_resource_images/", verbose_name="Banner Image", null=True
    )
    sub_title = models.TextField()
    overview_title = models.CharField(max_length=255, verbose_name="Overview Title")
    overview_description = models.TextField(verbose_name="Overview Description")
    # developer pricing
    developer_pricing_title = models.CharField(
        max_length=255, verbose_name="Title", null=True
    )
    developer_pricing_sub_title = models.CharField(
        max_length=255, verbose_name="Sub Title", null=True
    )
    # hiring process
    hiring_process_title = models.CharField(
        max_length=255, verbose_name="Title", null=True
    )
    hiring_process_sub_title = models.CharField(
        max_length=255, verbose_name="Sub Title", null=True
    )
    # FAQ
    faq_sub_title = models.TextField(verbose_name="Sub Title", null=True)
    
    # pricing table
    pricing_title = models.CharField(max_length=255, verbose_name="Title", null=True)
    pricing_sub_title = models.CharField(max_length=255, verbose_name="Sub Title", null=True)
    

    def __str__(self):
        return self.title


    class Meta:
        verbose_name = "Hire Developer"
        verbose_name_plural = "Hire Developers"

class HireResourceServiceContent(models.Model):
    hire_resource = models.ForeignKey(HireResourcePage,related_name='hire_resource',null=True,blank=True,on_delete=models.CASCADE)
    title = models.CharField(max_length=255,null=True,blank=True)
    content = HTMLField(null=True,blank=True)
    image = models.ImageField(upload_to="hire_resource_image",null=True,blank=True)

    def __str__(self):
        return self.title


class HireResourceService(models.Model):
    hire_resource = models.ForeignKey(
        HireResourcePage, related_name="services", on_delete=models.SET_NULL, null=True
    )
    title = models.CharField(max_length=255)
    short_description = models.TextField()
    description = HTMLField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"


class DeveloperPriceType(models.Model):
    criteria = models.ForeignKey(
        Criteria,
        related_name="developer_price_types",
        on_delete=models.SET_NULL,
        null=True,
    )
    hire_resource = models.ForeignKey(
        HireResourcePage,
        related_name="developer_price_types",
        on_delete=models.SET_NULL,
        null=True,
    )
    jr_developer = models.CharField(max_length=255)
    mid_developer = models.CharField(max_length=255)
    senior_developer = models.CharField(max_length=255)

    def __str__(self):
        return self.criteria.title

    class Meta:
        verbose_name = "Developer Price Criteria"
        verbose_name_plural = "Developer Price Criteria"


class FAQQuestion(models.Model):
    hire_process = models.ForeignKey(
        HireResourcePage, related_name="questions", on_delete=models.SET_NULL, null=True
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question



class HiringStep(models.Model):
    hiring_process = models.ForeignKey(
        HireResourcePage,
        related_name="steps",
        on_delete=models.SET_NULL,
        null=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.ImageField()

    def __str__(self):
        return self.title


class Cost(models.Model):
    hire_resource = models.ForeignKey(
        HireResourcePage, related_name="costs", on_delete=models.SET_NULL, null=True
    )
    cost_type = models.ForeignKey(
        CostType, related_name="costs", on_delete=models.SET_NULL, null=True
    )
    short_description = models.CharField(max_length=255, null=True)
    cost_amount = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.TextField()

    def __str__(self):
        return self.cost_type.cost_type
    
    
    class Meta:
        verbose_name = "Approx Cost"
        verbose_name_plural = "Approx Costs"


# ===========================================================================================

class HireDeveloperPage(models.Model):
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)
    featured_image = models.ImageField(upload_to="hire_developer_page", null=True, blank=True)

    class Meta:
        verbose_name = "Hire Developer"
        verbose_name_plural = "Hire Developer"


class DeliveryModuleIntro(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="delivery_module_intros", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Delivery Module Intro"
        verbose_name_plural = "Delivery Module Intro"



class WorkingMechanism(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="working_mechanisms", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)
    conclusion = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Working Mechanism"
        verbose_name_plural = "Working Mechanism"

class WorkingMechanismCards(models.Model):
    working_mechanism = models.ForeignKey(
        WorkingMechanism, related_name="working_mechanism_cards", on_delete=models.CASCADE, null=True, blank=True
    )
    order = models.PositiveIntegerField(default=0, help_text="Order of display for working mechanism cards", null=True, blank=True)
    description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Working Mechanism Card"
        verbose_name_plural = "Working Mechanism Cards"



class Benifits(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="benefits", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Benifit"
        verbose_name_plural = "Benifits"



class BenifitCards(models.Model):
    benifit = models.ForeignKey(
        Benifits, related_name="benifit_cards", on_delete=models.CASCADE, null=True, blank=True
    )
    icon = models.ImageField(upload_to="benifit_cards", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Benifit Card"
        verbose_name_plural = "Benifit Cards"



class HireDevelopersOurProcess(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="our_processes", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display for process steps")

    class Meta:
        verbose_name = "Our Process"
        verbose_name_plural = "Our Processes"



class HiringComparison(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="hiring_comparisons", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Hiring Comparison"
        verbose_name_plural = "Hiring Comparisons"


class HiringThroughMediusware(models.Model):
    hire_developer_page = models.ForeignKey(
        HiringComparison, related_name="hiring_through_mediuswares", on_delete=models.CASCADE, null=True, blank=True
    )
    description = HTMLField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Hiring Through Mediusware"
        verbose_name_plural = "Hiring Through Mediusware"


class HiringFreeLancer(models.Model):
    hiring_comparison = models.ForeignKey(
        HiringComparison, related_name="hiring_freelancers", on_delete=models.CASCADE, null=True, blank=True
    )
    description = HTMLField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Hiring FreeLancer"
        verbose_name_plural = "Hiring FreeLancer"


class ComprehensiveGuide(models.Model):
    hiring_comparison = models.ForeignKey(
        HireDeveloperPage, related_name="comprehensive_guides", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Comprehensive Guide"
        verbose_name_plural = "Comprehensive Guides"


class ComprehensiveGuideSections(models.Model):
    comprehensive_guide = models.ForeignKey(
        ComprehensiveGuide, related_name="comprehensive_guide_sections", on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Comprehensive Guide Section"
        verbose_name_plural = "Comprehensive Guide Sections"


class ComprehensiveGuideSectionQnA(models.Model):
    comprehensive_guide_section = models.ForeignKey(
        ComprehensiveGuideSections, related_name="comprehensive_guide_section_points", on_delete=models.CASCADE, null=True, blank=True
    )
    question = models.CharField(max_length=255, null=True, blank=True)
    answer = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Comprehensive Guide Section QnA"
        verbose_name_plural = "Comprehensive Guide Section QnA"


class DefiningDevelopers(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="defining_developer_roles", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Defining Developer"
        verbose_name_plural = "Defining Developers"


class DefiningDeveloperCards(models.Model):
    defining_developer_role = models.ForeignKey(
        DefiningDevelopers, related_name="defining_developer_cards", on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Defining Developer Card"
        verbose_name_plural = "Defining Developer Cards"


class Qualities(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="qualities", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)


    class Meta:
        verbose_name = "Quality"
        verbose_name_plural = "Qualities"
    

class QualityCards(models.Model):
    quality = models.ForeignKey(
        Qualities, related_name="quality_cards", on_delete=models.CASCADE, null=True, blank=True
    )
    icon = models.ImageField(upload_to="quality_cards", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "Quality Card"
        verbose_name_plural = "Quality Cards"


class HireDeveloperFAQ(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="faqs", on_delete=models.CASCADE, null=True, blank=True
    )
    question = models.CharField(max_length=255, null=True, blank=True)
    answer = HTMLField(null=True, blank=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ's"


class HireDeveloperMetaDescription(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="meta_descriptions", on_delete=models.CASCADE, null=True, blank=True
    )
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Meta"
        verbose_name_plural = "Meta"

















