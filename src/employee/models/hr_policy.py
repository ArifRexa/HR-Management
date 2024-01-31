from django.db import models

from tinymce.models import HTMLField

from config.model.TimeStampMixin import TimeStampMixin
from config.model.AuthorMixin import AuthorMixin


class HRPolicy(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    policy_file = models.FileField(upload_to='', default='')

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        verbose_name = "Set HR Policy"
        verbose_name_plural = "Set HR Policies"


class HRPolicySection(TimeStampMixin, AuthorMixin):
    hr_policy = models.ForeignKey(
        to=HRPolicy,
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=255)
    description = HTMLField()

    def __str__(self) -> str:
        return f"{self.title}"


class HRPolicyPublic(HRPolicy):
    class Meta:
        proxy = True
        verbose_name = "HR Contract Policy"
        verbose_name_plural = "HR Contract Policies"
