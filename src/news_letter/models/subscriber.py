import uuid
from django.db import models

from config.model.TimeStampMixin import TimeStampMixin
from news_letter.models.segments import Segment


class Subscriber(TimeStampMixin):
    segment = models.ForeignKey(
        Segment, on_delete=models.SET_NULL, null=True, blank=True, related_name='subscribers'
    )
    email = models.EmailField(unique=True)
    is_subscribed = models.BooleanField(default=True, blank=True)
    is_verified = models.BooleanField(default=False, blank=True)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)



    def __str__(self):
        return self.email