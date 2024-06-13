from django.db import models
from tinymce.models import HTMLField
from config.model.TimeStampMixin import TimeStampMixin

# Create your models here.

class MarketingSlider(TimeStampMixin):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField()
    image = models.ImageField(upload_to="marketing_slider")
    
    def __str__(self):
        return self.title if self.title else str(self.id)