from django.db import models

from config.model.TimeStampMixin import TimeStampMixin
from config.model.AuthorMixin import AuthorMixin

from .employee import Employee


class NeedHelpPosition(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=30, help_text="Ex. CTO, Tech Lead etc.")
    email = models.EmailField()
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.title}"


class EmployeeNeedHelp(TimeStampMixin, AuthorMixin):
    employee = models.OneToOneField(
        to=Employee,
        on_delete=models.CASCADE,
        limit_choices_to={"active": True},
    )
    need_help_position = models.ManyToManyField(
        to=NeedHelpPosition,
        limit_choices_to={"active": True},
        blank=True
    )
