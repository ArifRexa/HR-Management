from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee

class FavouriteMenu(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, limit_choices_to={'active': True})
    menu_link = models.CharField(max_length=255)
    menu_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.employee.full_name}" 