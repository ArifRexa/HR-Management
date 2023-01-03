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
