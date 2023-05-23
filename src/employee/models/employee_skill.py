from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee


class Skill(AuthorMixin, TimeStampMixin):
    title = models.CharField(unique=True, max_length=255)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class EmployeeSkill(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    percentage = models.FloatField(max_length=100)


class Learning(AuthorMixin, TimeStampMixin):
    asigned_to = models.ForeignKey(Employee,
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'project_eligibility': True, 'active': True},
                                   related_name='skill_acquisition_asigned_to')
    asigned_by = models.ForeignKey(Employee,
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'manager': True, 'active': True},
                                   related_name='skill_acquisition_asigned_by')
    details = models.TextField(blank=False, null=True)

    def __str__(self):
        return self.asigned_to.full_name
