from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField

class ServeCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    title_in_detail_page = models.CharField(max_length=100, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    industry_field_image = models.ImageField(upload_to='industry_serve_images/', blank=True, null=True)
    industry_banner = models.ImageField(upload_to='industry_banners/', blank=True, null=True)
    impressive_title = models.CharField(max_length=200, blank=True, null=True)
    impressive_description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Industry Detail"
        verbose_name_plural = "Industry Details"

class ApplicationAreas(models.Model):
    serve_category = models.ForeignKey(ServeCategory, related_name='application_areas', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = HTMLField()
    image = models.ImageField(upload_to='solutions_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class IndustryServe(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    banner_image = models.ImageField(upload_to='industry_image_cover/', blank=True, null=True)
    motivation_title = models.CharField(max_length=200)
    motivation_description = models.TextField()
    serve_categories = models.ManyToManyField(ServeCategory, related_name='industries')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Industry"
        verbose_name_plural = "Industries"