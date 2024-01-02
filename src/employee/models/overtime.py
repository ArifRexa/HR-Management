from django.db import models
from django.template.defaultfilters import truncatewords

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee


class Overtime(TimeStampMixin, AuthorMixin):
    class Meta:
        permissions = [
            ('can_approve_overtime', 'Can Approve Overtime'),
        ]

    STATUS_CHOICE = (
        ('pending', '⌛ Pending'),
        ('approved', '👍 Approved'),
        ('rejected', '⛔ Rejected'),
    )
    date = models.DateField(null=False, help_text='Date of overtime')
    note = models.TextField(null=True, help_text='Please explain the reason for overtime')
    employee = models.ForeignKey(Employee, limit_choices_to={'active': True}, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')

    def __str__(self):
        return self.employee.full_name

    def short_note(self):
        return truncatewords(self.note, 10)
