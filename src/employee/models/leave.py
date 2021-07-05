from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import models
from django.template.defaultfilters import truncatewords
from django_q.tasks import async_task

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.model_mixin.LeaveMixin import LeaveMixin
from employee.models.employee import Employee


class Leave(TimeStampMixin, AuthorMixin, LeaveMixin):
    message = models.TextField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    status_changed_by = models.ForeignKey(User, limit_choices_to={'is_superuser': True}, null=True,
                                          on_delete=models.RESTRICT)
    status_changed_at = models.DateField(null=True)

    @property
    def short_message(self):
        return truncatewords(self.message, 10)

    def save(self, *args, **kwargs):
        super(Leave, self).save(*args, **kwargs)


class LeaveAttachment(TimeStampMixin, AuthorMixin):
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
    attachment = models.FileField(help_text='Image , PDF or Docx file ')
