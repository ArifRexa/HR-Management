from django.db import models

from tinymce.models import HTMLField
from config.model.TimeStampMixin import TimeStampMixin


class IndustryWeServeModelManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_active=True)


class IndustryPage(TimeStampMixin):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    sub_title = models.TextField(blank=True, null=True)
    short_description = models.TextField()
    description = models.TextField()
    image = models.ImageField(upload_to="industry_we_serve")
    is_active = models.BooleanField(default=True)

    objects = IndustryWeServeModelManager()

    def __str__(self):
        return self.title


class IndustryWeServe(TimeStampMixin):
    page = models.ForeignKey(IndustryPage, on_delete=models.CASCADE, related_name="industry_we_serve")
    slug = models.SlugField(unique=True, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="industry_we_serve_content")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class IndustryWeServeContent(TimeStampMixin):
    industry = models.ForeignKey(IndustryWeServe, on_delete=models.CASCADE, related_name="industry_we_serve_contents")
    slug = models.SlugField(unique=True, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    content = HTMLField(null=True, blank=True)
    image = models.ImageField(upload_to="industry_we_serve_content")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
