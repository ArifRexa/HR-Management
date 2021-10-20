from django.db import models

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin


class SMSPromotion(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    sms_body = models.TextField(help_text="{full_name}=> Candidate Full Name, {candidate_job} => Candidate Job")
    is_default = models.BooleanField(default=True)

    def __str__(self):
        return self.title
