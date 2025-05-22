from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee
from django.utils import timezone
import calendar
from django.core.validators import MaxValueValidator



def get_current_month():
    return timezone.now().month
def get_current_year():
    return timezone.now().year

class EmployeeRating(TimeStampMixin, AuthorMixin):

    if timezone.now().month == 1:  
        YEAR_CHOICES = [(timezone.now().year-1, timezone.now().year-1), (timezone.now().year, timezone.now().year)]  
    else:
        YEAR_CHOICES = [(timezone.now().year, timezone.now().year)] 
    MONTH_CHOICE = [(m,calendar.month_name[m]) for m in range(1,timezone.now().month + 1)]

    score = models.SmallIntegerField(help_text="Max Score Will be 25", default=0, validators=[MaxValueValidator(25)], blank=True, null=True)
    employee = models.ForeignKey(Employee, limit_choices_to={"active": True}, on_delete=models.CASCADE)
    # project = models.ForeignKey(Project, limit_choices_to={"active": True}, on_delete=models.SET_NULL, null=True, blank=True)
    # feedback_responsiveness = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    # continuous_learning = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    # collaboration = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    # communication_effectiveness = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    # leadership_potential = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    # problem_solving_ability = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    # innovation_and_creativity = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    # adaptability_and_flexibility = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    # professional_growth_and_development = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    # overall_contribution_to_team_success = models.IntegerField(choices=list(zip(range(0, 11), range(0, 11))), default=0)
    comment = models.TextField(null=True, blank=True)
    month = models.IntegerField(choices=MONTH_CHOICE, default=get_current_month)
    year = models.IntegerField(choices=YEAR_CHOICES, default=get_current_year)

    rating_overall_satisfaction = models.FloatField(blank=True, null=True)
    communication_effectiveness = models.FloatField(blank=True, null=True)
    rating_quality_of_work = models.FloatField(blank=True, null=True)
    rating_time_management = models.FloatField(blank=True, null=True)
    rating_understanding_of_requirements = models.FloatField(blank=True, null=True)
    overall_contribution_to_team_success = models.FloatField(blank=True, null=True)
    professional_growth_and_development = models.FloatField(blank=True, null=True)
    problem_solving_ability = models.FloatField(blank=True, null=True)
    collaboration = models.FloatField(blank=True, null=True)
    leadership_potential = models.FloatField(blank=True, null=True)
    adaptability_and_flexibility = models.FloatField(blank=True, null=True)


    class Meta:
        verbose_name = "Employee Rating"
        verbose_name_plural = "Employee Ratings"
        permissions = [
            ("can_view_all_ratings", "Can View All Ratings Provided"),
        ]
    

    def save(self, *args, **kwargs):
        # Calculate the average score
        # total_score = (
        #     self.feedback_responsiveness +
        #     self.continuous_learning +
        #     self.collaboration +
        #     self.communication_effectiveness +
        #     self.leadership_potential +
        #     self.problem_solving_ability +
        #     self.innovation_and_creativity +
        #     self.adaptability_and_flexibility +
        #     self.professional_growth_and_development +
        #     self.overall_contribution_to_team_success
        # )
        # num_fields = 10  # Number of fields contributing to the score
        # self.score = total_score / num_fields

        # Call the save method of the parent class to save the object
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.employee.full_name

# @receiver(post_save, sender=EmployeeRating)
# def employee_rating_bonus(sender, instance, created, **kwargs):
   
#     if created:
#         bonus_project_hour = ProjectHour()
#         bonus_project_hour.manager = Employee.objects.filter(id=30).first()
#         bonus_project_hour.hours = 1
#         bonus_project_hour.hour_type = 'bonus'
#         bonus_project_hour.date = timezone.now()
#         bonus_project_hour.project = Project.objects.filter(id=20).first()
#         bonus_project_hour.save()

#         employee_project_hour = EmployeeProjectHour()
#         employee_project_hour.project_hour = bonus_project_hour
#         employee_project_hour.hours = 1

#         user = User.objects.get(pk=instance.created_by_id)
#         employee = Employee.objects.get(user=user)

#         employee_project_hour.employee = employee
#         employee_project_hour.save()

#     else:
#         print("An existing instance of MyModel was updated by user:")

    # You can perform additional actions here based on the saved instance