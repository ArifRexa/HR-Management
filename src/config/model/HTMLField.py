from django.db import models


class HTMLField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'widget': ''}
