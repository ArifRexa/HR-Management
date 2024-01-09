from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee
from django.core.exceptions import ValidationError
from datetime import datetime

class SQARating(TimeStampMixin, AuthorMixin):
    score = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    sqa = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="sqa_employee")
    comment = models.TextField()

    class Meta:
        verbose_name = "SQA Rating"
        verbose_name_plural = "SQA Rating List"

    def __str__(self) -> str:
        return self.sqa.full_name
    
    def clean(self):
        if datetime.now().weekday() != 4:
            raise ValidationError({"comment": "You can\'t make rating today. You can try at friday."})
