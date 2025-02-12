from django.db import models

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin

# Create your models here.


class ClientMeeting(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(
        "project_management.Project",
        on_delete=models.CASCADE,
        limit_choices_to={"active": True},
    )
    start_time = models.DateTimeField()
