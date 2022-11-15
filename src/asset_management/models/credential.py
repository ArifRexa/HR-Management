from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin


class CredentialCategory(AuthorMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Credential(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(CredentialCategory, on_delete=models.RESTRICT)
    description = HTMLField()
    privileges = models.ManyToManyField(User, blank=True)

    class Meta:
        permissions = [
            ("access_all_credentials", "Can able to see all credentials")
        ]
