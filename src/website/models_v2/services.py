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
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    sub_title = models.TextField()
    # image = models.ImageField(upload_to="service_page_image")
    banner_query = models.CharField(max_length=255)
    development_services_title = models.CharField(max_length=255, verbose_name="Title")
    development_services_sub_title = models.TextField(verbose_name="Sub Title")
    faq_short_description = models.TextField(verbose_name="Short Description")
    comparative_analysis_title = models.CharField(max_length=255, verbose_name="Title")
    comparative_analysis_sub_title = models.TextField(verbose_name="Sub Title")
    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"


class DiscoverOurService(TimeStampMixin):
    services = models.ForeignKey(
        ServicePage,
        related_name="discover_services",
        on_delete=models.SET_NULL,
        null=True,
    )
    title = models.CharField(max_length=255)
    short_description = models.TextField()
    description = HTMLField()

    def __str__(self):
        return self.title


class DevelopmentServiceProcess(TimeStampMixin):
    services = models.ForeignKey(
        ServicePage,
        related_name="development_services_process",
        on_delete=models.SET_NULL,
        null=True,
    )
    title = models.CharField(max_length=255)
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
        max_length=255, verbose_name="Sapphire Software Solutions"
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
    answer = models.TextField()

    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name = "Service FAQ"
        verbose_name_plural = "Service FAQs"