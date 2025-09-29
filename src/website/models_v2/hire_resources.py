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


class DeliveryModuleIntro(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="delivery_module_intros", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)

class WorkingMechanism(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="working_mechanisms", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)

class Benifits(models.Model):
    hire_developer_page = models.ForeignKey(
        HireDeveloperPage, related_name="benefits", on_delete=models.CASCADE, null=True, blank=True
    )
    seo_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)

class BenifitCards(models.Model):
    benifit = models.ForeignKey(
        Benifits, related_name="benifit_cards", on_delete=models.CASCADE, null=True, blank=True
    )
    icon = models.ImageField(upload_to="benifit_cards", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
















