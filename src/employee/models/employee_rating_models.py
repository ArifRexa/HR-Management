from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from project_management.models import Project

class EmployeeRating(TimeStampMixin, AuthorMixin):
    score = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField()

    class Meta:
        verbose_name = "Employee Rating"
        verbose_name_plural = "Employee Ratings"

    def __str__(self) -> str:
        return self.employee.full_name
    
    def clean(self):
        is_provided = EmployeeRating.objects.filter(created_at__month=datetime.now().month, employee=self.employee).exists()
        if is_provided and self.id == None:
            raise ValidationError({'employee': 'You already given the rating'})
    
        delete_or_update_before = datetime.now() + timedelta(days=7)
        if self.id != None and self.created_at > delete_or_update_before:
            raise ValidationError({"comment": "You can\'t update your rating!"})
        
        if datetime.now().weekday() != 4:
            raise ValidationError({"comment": "You can\'t make rating today. You can try at friday."})
