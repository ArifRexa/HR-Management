from django.db import models
from tinymce.models import HTMLField

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee

class SocialMedia(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=200, blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class EmployeeSocial(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    social_name = models.ForeignKey(SocialMedia, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    url = models.URLField()


class EmployeeContent(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = HTMLField()
