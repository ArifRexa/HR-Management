from django.db import models

from config.model.AuthorMixin import AuthorMixin


class Profession(AuthorMixin):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Contact(AuthorMixin):
    name = models.CharField(max_length=155)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    phone = models.TextField(help_text='phone number separate by comma (,)')
    address = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
