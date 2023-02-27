from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee
from django.template.defaultfilters import truncatewords



class ExcuseNote(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    excuse_acts = models.TextField()

    def __str__(self) -> str:
        return f"{self.employee.full_name}"

    # def short_excuse_acts(self):
    #     return truncatewords(self.excuse_acts, 10)
    
    class Meta:
        verbose_name = 'Excuse note'
        verbose_name_plural = 'Excuse notes'