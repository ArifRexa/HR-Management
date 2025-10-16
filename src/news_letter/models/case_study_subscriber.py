from django.db import models

from config.model.TimeStampMixin import TimeStampMixin
from project_management.models import Project

# Create your models here.

class CaseStudySubscriber(TimeStampMixin):
    email = models.EmailField()
    project_title = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='case_study_subscribers')
    is_subscribed = models.BooleanField(default=True, blank=True)
    
    def __str__(self):
        return self.email