from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import ValidationError
from django.template.defaultfilters import truncatewords
from django.db.models import Q
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.leave.LeaveMixin import LeaveMixin
from employee.models.employee import Employee


# TODO : leave calculation by permanent date
# TODO : leave in cash in every january
class Leave(TimeStampMixin, AuthorMixin, LeaveMixin):
    message = models.TextField(validators=[MinLengthValidator(150)])
    status_changed_by = models.ForeignKey(
        User,
        limit_choices_to={"is_superuser": True},
        null=True,
        on_delete=models.RESTRICT,
    )
    status_changed_at = models.DateField(null=True)

    @property
    def short_message(self):
        return truncatewords(self.message, 10)

    def __str__(self):
        return f"{self.employee.full_name} : {self.created_at.strftime('%Y-%m-%d %I:%M %P')}"
    
    # def get_leave_feedback(self):
    #     print(self.leavefeedback_set.all())
    
    def management__feedback(self):
        feedbacks = self.leavefeedback_set.all()
        # feedback_list = [feedback.feedback for feedback in feedbacks]
        total_feedback = ""
        for feedback in feedbacks:
            total_feedback += feedback.feedback
        return total_feedback

    class Meta:
        permissions = (
            (
                "can_approve_leave_applications",
                "Can able to approve leave applications",
            ),
            (
                "can_add_leave_at_any_time",
                "Can able to add leave at any time",
            ),
            (
                "can_update_after_approve",
                "Can able to update after approve",
            ),
        )


class LeaveFeedback(TimeStampMixin, AuthorMixin):

    feedback = models.TextField(null=True, blank=True)
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Management Feedback'
        verbose_name_plural = 'Management Feedbacks'



class LeaveAttachment(TimeStampMixin, AuthorMixin):
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
    attachment = models.FileField(help_text="Image , PDF or Docx file ")


class LeaveManagement(TimeStampMixin):
    LEAVE_STATUS = (
        ("pending", "⏳ Pending"),
        ("approved", "\u2705 Approved"),
        ("rejected", "⛔ Rejected"),
        ("need_action", "🤔 Need Further Discussion"),
    )


    leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to=(Q(active=True) & (Q(manager=True) | Q(lead=True))),
        related_name="leave_management_manager",
    )
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default="pending")
    approval_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.leave.employee.full_name} : {self.manager.full_name}"

    class Meta:
        verbose_name = "Leave Approval"
        verbose_name_plural = "Leave Approvals"
