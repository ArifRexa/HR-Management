from django.db import models
from employee.models import Employee
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from django.utils import timezone
import datetime

class TourAllowance(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    expense_per_person = models.PositiveIntegerField()
    employees = models.ManyToManyField(Employee, limit_choices_to={'active': True}, blank=True)
    tour_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title
