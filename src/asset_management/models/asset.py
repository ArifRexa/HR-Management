from django.db import models

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin


class AssetCategory(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Asset(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
