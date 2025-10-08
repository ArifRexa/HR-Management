from django.db import models

from config.model.TimeStampMixin import TimeStampMixin

# Create your models here.

class Segment(TimeStampMixin):
    title = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True, blank=True)
    
    def __str__(self):
        return self.title