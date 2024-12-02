from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import truncatewords
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee


class Resignation(TimeStampMixin, AuthorMixin):
    STATUS_CHOICE = (
        ("pending", "⏳ Pending"),
        ("approved", "✔ Approved"),
        ("rejected", "⛔ Rejected"),
    )
    message = models.TextField(max_length=1000)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=25, default="pending", choices=STATUS_CHOICE)
    approved_at = models.DateField(null=True, editable=False)
    approved_by = models.ForeignKey(
        User,
        limit_choices_to={"is_superuser": True},
        null=True,
        on_delete=models.RESTRICT,
        editable=False,
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        limit_choices_to={"user__is_superuser": False, "active": True},
    )

    class Meta:
        permissions = (
            (
                "can_view_all_resignations",
                "Can View All Resignations",
            ),
        )

    def short_message(self):
        return truncatewords(self.message, 20)


class ResignationFeedback(TimeStampMixin, AuthorMixin):
    resignation = models.ForeignKey(Resignation, on_delete=models.CASCADE)
    message = models.TextField(max_length=1000)
    feedback_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        editable=False,
    )
