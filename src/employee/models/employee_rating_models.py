from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import datetime, timedelta
from project_management.models import Project, DailyProjectUpdate, Employee, Project

class EmployeeRating(TimeStampMixin, AuthorMixin):

    score = models.FloatField()
    employee = models.ForeignKey(Employee, limit_choices_to={"active": True}, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, limit_choices_to={"active": True}, on_delete=models.SET_NULL, null=True, blank=True)
    performance_quality = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    efficiency = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    collaboration = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    communication_effectiveness = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    leadership_potential = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    problem_solving_ability = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    innovation_and_creativity = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    adaptability_and_flexibility = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    professional_growth_and_development = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    overall_contribution_to_team_success = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), default=1)
    comment = models.TextField()
    class Meta:
        verbose_name = "Employee Rating"
        verbose_name_plural = "Employee Ratings"
        permissions = [
            ('can_view_all_ratings', 'Can View All Ratings Provided'),
        ]
    

    def save(self, *args, **kwargs):
        # Calculate the average score
        total_score = (
            self.performance_quality +
            self.efficiency +
            self.collaboration +
            self.communication_effectiveness +
            self.leadership_potential +
            self.problem_solving_ability +
            self.innovation_and_creativity +
            self.adaptability_and_flexibility +
            self.professional_growth_and_development +
            self.overall_contribution_to_team_success
        )
        num_fields = 10  # Number of fields contributing to the score
        self.score = total_score / num_fields

        # Call the save method of the parent class to save the object
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.employee.full_name

@receiver(post_save, sender=EmployeeRating)
def employee_rating_bonus(sender, instance, created, **kwargs):
   
    if created:
        daily_project_update = DailyProjectUpdate()
        daily_project_update.employee = Employee.objects.filter(id=instance.created_by_id).first()
        daily_project_update.manager = Employee.objects.filter(id=30).first()
        daily_project_update.hours = 1
        daily_project_update.update = 'You get this bonus for employee ratings'
        daily_project_update.status = 'approved'
        daily_project_update.project = Project.objects.filter(id=20).first()
        daily_project_update.save()
    else:
        print("An existing instance of MyModel was updated by user:")

    # You can perform additional actions here based on the saved instance