from django.db import models

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee


class EmployeeFeedback(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    feedback = models.TextField()
    avg_rating = models.FloatField()
    environmental_rating = models.FloatField()
    facilities_rating = models.FloatField()
    learning_growing_rating = models.FloatField()
    happiness_index_rating = models.FloatField()
    boss_rating = models.FloatField()

    @property
    def has_red_rating(self):
        red_line = 3.5

        return self.environmental_rating <= red_line \
            or self.facilities_rating <= red_line \
            or self.learning_growing_rating <= red_line \
            or self.happiness_index_rating <= red_line \
            or self.boss_rating <= red_line

    class Meta:
        permissions = (
            ("can_see_employee_feedback_admin", "Can able to see emloyee feedback admin"),
        )

    def save(self, *args, **kwargs):
        avg_rating = self.environmental_rating + self.facilities_rating + self.learning_growing_rating + self.happiness_index_rating + self.boss_rating
        avg_rating = round(avg_rating/5, 1)
        self.avg_rating = avg_rating
        super(EmployeeFeedback, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.employee.full_name} ({str(self.avg_rating)})"

class CommentAgainstEmployeeFeedback(TimeStampMixin, AuthorMixin):
    employee_feedback = models.ForeignKey(EmployeeFeedback,on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)

    class Meta:
        ordering = ('-created_at',)




from django.utils.translation import gettext_lazy as _


class EmployeePerformanceFeedback(TimeStampMixin, AuthorMixin):
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        help_text=_("The employee being evaluated for performance.")
    )
    technical_skill = models.SmallIntegerField(
        choices=RATING_CHOICES,
        help_text=_(
            "Technical/Functional Skills rating (1-5). Weight: 40%. "
        )
    )
    project_deliver = models.SmallIntegerField(
        choices=RATING_CHOICES,
        help_text=_(
            "Project Deliverables rating (1-5). Weight: 30%. "
        )
    )
    client_feedback = models.SmallIntegerField(
        choices=RATING_CHOICES,
        help_text=_(
            "Peer/Client Feedback rating (1-5). Weight: 20%. "
        )
    )
    initiative_learning = models.SmallIntegerField(
        choices=RATING_CHOICES,
        help_text=_(
            "Initiative & Learning rating (1-5). Weight: 10%. "
        )
    )

    class Meta:
        verbose_name = _("Employee Feedback")
        verbose_name_plural = _("Employee Feedbacks")
        ordering = ('-created_at',)

    @property
    def technical_skill_score(self):
        """Calculate weighted score for Technical/Functional Skills (40%)."""
        return self.technical_skill * 0.4

    @property
    def project_deliver_score(self):
        """Calculate weighted score for Project Deliverables (30%)."""
        return self.project_deliver * 0.3

    @property
    def client_feedback_score(self):
        """Calculate weighted score for Peer/Client Feedback (20%)."""
        return self.client_feedback * 0.2

    @property
    def initiative_learning_score(self):
        """Calculate weighted score for Initiative & Learning (10%)."""
        return self.initiative_learning * 0.1

    @property
    def overall_score(self):
        """Calculate the overall performance score (out of 5)."""
        return (
            self.technical_skill_score +
            self.project_deliver_score +
            self.client_feedback_score +
            self.initiative_learning_score
        )

    @property
    def rating_definition(self):
        """Return the rating definition based on the overall score."""
        score = self.overall_score
        if score >= 4.5:
            return "Exceptional"
        elif score >= 3.5:
            return "Exceeds"
        elif score >= 2.5:
            return "Meets"
        elif score >= 1.5:
            return "Needs Improvement"
        else:
            return "Unsatisfactory"

    @property
    def eligible_for_promotion(self):
        """Determine promotion eligibility based on the overall score."""
        score = self.overall_score
        if score >= 4.5:
            return "Yes (fast-track considered)"
        elif score >= 3.5:
            return "Yes"
        else:
            return "No"

    @property
    def probation_risk(self):
        """Determine if the employee is at risk of probation."""
        return self.overall_score < 1.5