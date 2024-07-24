from django.db import models
from django.utils.text import slugify

class ServeCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    short_description = models.TextField(blank=True, null=True)
    impressive_title = models.CharField(max_length=200, blank=True, null=True)
    impressive_description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ApplicationAreas(models.Model):
    serve_category = models.ForeignKey(ServeCategory, related_name='application_areas', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title
