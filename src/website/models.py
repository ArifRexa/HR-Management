from django.db import models

# Create your models here.
from config.model.HTMLField import HTMLField
from project_management.models import Client, Technology


class Service(models.Model):
    icon = models.ImageField()
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    banner_image = models.ImageField()
    feature_image = models.ImageField()
    feature = HTMLField()
    technologies = models.ManyToManyField(Technology)
    clients = models.ManyToManyField(Client)
    order = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
