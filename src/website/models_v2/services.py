from django.db import models
from tinymce.models import HTMLField

from config.model.TimeStampMixin import TimeStampMixin


class ServicePage(TimeStampMixin):
    is_parent = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self",
        related_name="children",
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"is_parent": True},
        blank=True,
    )
    icon = models.ImageField(upload_to="service_page/icons", null=True, blank=True)
    feature_image = models.ImageField(
        upload_to="service_page/feature_images", null=True, blank=True
    )
    title = models.CharField(max_length=255)
    h1_title = models.CharField(max_length=255, verbose_name="H1 Title", null=True, blank=True)
    slug = models.SlugField(unique=True)
    sub_title = models.TextField(verbose_name="Section Title")
    description = HTMLField(null=True, blank=True, verbose_name="Section Description")
    menu_title = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Section Title"
    )
    # image = models.ImageField(upload_to="service_page_image")
    banner_query = models.CharField(max_length=255)
    development_services_title = models.CharField(max_length=255, verbose_name="Section Title")
    development_services_sub_title = models.TextField(verbose_name="Section Description")
    faq_short_description = models.TextField(verbose_name="Short Description")
    comparative_analysis_title = models.CharField(max_length=255, verbose_name="Section Title")
    comparative_analysis_sub_title = models.TextField(verbose_name="Section Description")
    why_choose_us_sub_title = models.TextField(
        verbose_name="Section Description", null=True, blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

# ======================= SolutionsAndServices =======================
class SolutionsAndServices(TimeStampMixin):
    services = models.ForeignKey(
        ServicePage,
        related_name="solutions_and_services",
        on_delete=models.SET_NULL,
        null=True,
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True)
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)

    def __str__(self):
        return self.section_title
    

class SolutionsAndServicesCards(TimeStampMixin):
    solutions_and_services = models.ForeignKey(
        SolutionsAndServices,
        related_name="cards",
        on_delete=models.SET_NULL,
        null=True,
    )
    card_title = models.CharField(max_length=200, blank=True, null=True)
    card_description = HTMLField(blank=True, null=True)
    image = models.ImageField(upload_to='industry_details_images/', blank=True, null=True)

    def __str__(self):
        return self.card_title

# =====================================Key Things======================================

class KeyThings(models.Model):
    industry = models.ForeignKey(
        ServicePage, 
        on_delete=models.CASCADE,
        related_name='KeyThings',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True)
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)
    image = models.ImageField(upload_to='benefits_images/', blank=True, null=True)


    def __str__(self):
        return self.section_title or "Benefits"
    
    class Meta:
        verbose_name = "Key Things"
        verbose_name_plural = "Key Things"

class KeyThingsQA(models.Model):
    benefits = models.ForeignKey(
        KeyThings, 
        on_delete=models.CASCADE,
        related_name='KeyThings_cards',
        null=True,
        blank=True
    )
    card_title = models.CharField(max_length=200, blank=True, null=True)
    card_description = HTMLField(blank=True, null=True)
    def __str__(self):
        return self.card_title



# ========================== Best Practices ==========================
class BestPracticesHeadings(TimeStampMixin):
    service_page = models.ForeignKey(
        ServicePage,
        related_name="best_practices",
        on_delete=models.SET_NULL,
        null=True,
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True)
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)

    def __str__(self):
        return self.section_title   

class BestPracticesCards(TimeStampMixin):
    best_practices = models.ForeignKey(
        BestPracticesHeadings,
        related_name="cards",
        on_delete=models.SET_NULL,
        null=True,
    )
    card_title = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.card_title
    
class BestPracticesCardsDetails(TimeStampMixin):
    best_practices_cards = models.ForeignKey(
        BestPracticesCards,
        related_name="details",
        on_delete=models.SET_NULL,
        null=True,
    )
    card_title = models.CharField(max_length=200, blank=True, null=True)
    card_description = HTMLField(blank=True, null=True)

    def __str__(self):
        return self.card_title

# ================================= Why choose us =================================

class ServicesWhyChooseUs(TimeStampMixin):
    service_page = models.ForeignKey(
        ServicePage,
        related_name="why_choose_us",
        on_delete=models.SET_NULL,
        null=True,
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True)
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)

    def __str__(self):
        return self.section_title or "Why Choose Us"
    
class ServicesWhyChooseUsCards(TimeStampMixin):
    services_why_choose_us = models.ForeignKey(
        ServicesWhyChooseUs,
        related_name="cards",
        on_delete=models.SET_NULL,
        null=True,
    )
    icon = models.ImageField(upload_to='why_choose_us_images/', blank=True, null=True)
    card_title = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display for process steps")
    def __str__(self):
        return self.card_title
    
class ServicesWhyChooseUsCardsDetails(TimeStampMixin):
    services_why_choose_us_cards = models.ForeignKey(
        ServicesWhyChooseUsCards,
        related_name="details",
        on_delete=models.SET_NULL,
        null=True,
    )
    card_description = HTMLField(blank=True, null=True)

    def __str__(self):
        return self.card_description

# ================================= Our Process =================================

class ServicesOurProcess(models.Model):
    industry = models.ForeignKey(
        ServicePage, 
        on_delete=models.CASCADE,
        related_name='our_process',
        null=True,
        blank=True
    )
    section_title = models.CharField(max_length=200)
    section_description = HTMLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display for process steps")

    def __str__(self):
        return self.section_title
    
    class Meta:
        verbose_name = "Our Process"
        verbose_name_plural = "Our Processes"
        ordering = ['order']








class ServicePageFAQSchema(models.Model):
    service_page = models.OneToOneField(
        ServicePage, 
        on_delete=models.CASCADE, 
        related_name='faq_schema'
    )
    faq_schema = models.TextField(
        help_text="JSON-LD schema for FAQs"
    )

    def __str__(self):
        return f"FAQ Schema for {self.service_page.title}"



class ServicePageCTA(TimeStampMixin):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    button_link = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="cta_images/", null=True, blank=True)
    blog = models.ForeignKey(
        ServicePage, 
        on_delete=models.CASCADE, 
        related_name="ctas", 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.title or "CTA"


class DiscoverOurService(TimeStampMixin):
    services = models.ForeignKey(
        ServicePage,
        related_name="discover_services",
        on_delete=models.SET_NULL,
        null=True,
    )
    title = models.CharField(max_length=255, verbose_name="Section Title")
    short_description = models.TextField(verbose_name="Section Description")
    description = HTMLField()

    def __str__(self):
        return self.title


class AdditionalServiceContent(models.Model):
    services = models.ForeignKey(
        ServicePage,
        related_name="additional_service_content",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name="Section Title")
    content = HTMLField(null=True, blank=True)
    image = models.ImageField(upload_to="service_content_image", null=True, blank=True)

    def __str__(self):
        return self.title


class DevelopmentServiceProcess(TimeStampMixin):
    services = models.ForeignKey(
        ServicePage,
        related_name="development_services_process",
        on_delete=models.SET_NULL,
        null=True,
    )
    title = models.CharField(max_length=255, verbose_name="Section Title")
    short_description = models.TextField()
    icon = models.ImageField(upload_to="development_service_icon")

    def __str__(self):
        return self.title


class ServiceCriteria(TimeStampMixin):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ComparativeAnalysis(TimeStampMixin):
    criteria = models.ForeignKey(
        ServiceCriteria,
        related_name="developer_price_types",
        on_delete=models.SET_NULL,
        null=True,
    )
    services = models.ForeignKey(
        ServicePage,
        related_name="comparative_analysis",
        on_delete=models.SET_NULL,
        null=True,
    )
    sapphire_software_solutions = models.CharField(
        max_length=255, verbose_name="Mediusware Software Solutions"
    )
    in_house = models.CharField(max_length=255, verbose_name="In-House")
    freelance = models.CharField(max_length=255, verbose_name="Freelance")

    def __str__(self):
        return self.criteria.title


class ServiceFAQQuestion(models.Model):
    services = models.ForeignKey(
        ServicePage, related_name="questions", on_delete=models.SET_NULL, null=True
    )
    question = models.CharField(max_length=255)
    answer = HTMLField()

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "Service FAQ"
        verbose_name_plural = "Service FAQs"


class ServiceMetaData(models.Model):
    services = models.OneToOneField(
        ServicePage, related_name="service_meta_data", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255, verbose_name="Section Title")
    description = models.TextField()

    def __str__(self):
        return self.title
