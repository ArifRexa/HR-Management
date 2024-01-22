from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from project_management.models import Project


class EmployeeRating(TimeStampMixin, AuthorMixin):
    score = models.IntegerField(
        choices=list(zip(range(1, 11), range(1, 11))), default=1
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True
    )
    comment = models.TextField()

    class Meta:
        verbose_name = "Employee Rating"
        verbose_name_plural = "Employee Ratings"
        permissions = [
            ("can_view_all_ratings", "Can View All Ratings Provided"),
        ]

    def __str__(self) -> str:
        return self.employee.full_name
