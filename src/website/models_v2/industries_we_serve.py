from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField

from config.model import TimeStampMixin

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

class ServeCategoryCTA(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    button_link = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="cta_images/", null=True, blank=True)
    blog = models.ForeignKey(
        ServeCategory, 
        on_delete=models.CASCADE, 
        related_name="ctas", 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or "CTA"

    

class ServiceCategoryFAQ(models.Model):
    serve_category = models.ForeignKey(ServeCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = HTMLField()
    order = models.PositiveIntegerField(default=0, help_text="Order of display for FAQs")

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ's"

        ordering = ['order']


class ServeCategoryFAQSchema(models.Model):
    serve_category = models.OneToOneField(
        ServeCategory, 
        on_delete=models.CASCADE, 
        related_name='faq_schema'
    )
    faq_schema = models.TextField(
        help_text="JSON-LD schema for FAQs"
    )

    def __str__(self):
        return f"FAQ Schema for {self.serve_category.title}"



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