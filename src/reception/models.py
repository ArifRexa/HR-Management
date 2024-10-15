from django.db import models

from config.model.TimeStampMixin import TimeStampMixin

# Create your models here.
class Reception(TimeStampMixin):
    AGENDA_CHOICE = [
        ('interview','Interview'),
        ('meeting','Meeting'),
    ]
    name = models.CharField(max_length=255)
    agenda = models.CharField(max_length=20,choices=AGENDA_CHOICE,null=True,blank=True)
    comment = models.TextField(null=True,blank=True)

    def __str__(self):
        return f'{self.name} - {self.agenda}'
    
    