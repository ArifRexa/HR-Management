from django.db import models

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee


class EmployeeFeedback(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    feedback = models.TextField()
    rating = models.FloatField()

    def __str__(self) -> str:
        return f"{self.employee.full_name} ({str(self.rating)})"
