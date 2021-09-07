from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import truncatewords

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.leave.LeaveMixin import LeaveMixin
from employee.models.employee import Employee


# TODO : leave calculation by permanent date
# TODO : leave in cash in every january
class Leave(TimeStampMixin, AuthorMixin, LeaveMixin):
    message = models.TextField()
    employee = models.ForeignKey(Employee, limit_choices_to={'active': True}, on_delete=models.CASCADE)
    status_changed_by = models.ForeignKey(User, limit_choices_to={'is_superuser': True}, null=True,
                                          on_delete=models.RESTRICT)
    status_changed_at = models.DateField(null=True)

    @property
    def short_message(self):
        return truncatewords(self.message, 10)


class LeaveAttachment(TimeStampMixin, AuthorMixin):
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
    attachment = models.FileField(help_text='Image , PDF or Docx file ')
