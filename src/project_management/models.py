from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum

from config.model.TimeStampMixin import TimeStampMixin
from config.model.AuthorMixin import AuthorMixin
from employee.models import Employee


class Client(TimeStampMixin, AuthorMixin):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=80)
    address = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# Create your models here.
class Project(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=200)
    description = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ProjectHour(TimeStampMixin, AuthorMixin):
    manager = models.ForeignKey(Employee, limit_choices_to={'manager': True}, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, limit_choices_to={'active': True}, on_delete=models.SET_NULL, null=True,
                                blank=True)
    date = models.DateField()
    hours = models.FloatField()
    description = models.TextField(blank=True)
    payable = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.project} | {self.manager}"

    def save(self, *args, **kwargs):
        if not self.manager.manager:
            self.payable = False
        super(ProjectHour, self).save(*args, **kwargs)

    def employee_hour(self, employee_id):
        total = self.employeeprojecthour_set.aggregate(Sum('hours'))
        return employee_id, total['hours__sum']


class EmployeeProjectHour(TimeStampMixin, AuthorMixin):
    project_hour = models.ForeignKey(ProjectHour, on_delete=models.CASCADE)
    hours = models.FloatField()
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT,
                                 limit_choices_to={'manager': False, 'active': True})

    class Meta:
        permissions = [
            ("change_recent_activity", "Can change if inserted recently (3days)")
        ]


class DurationUnit(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=200)
    duration = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ProjectResource(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, limit_choices_to={'active': True}, on_delete=models.CASCADE)
    manager = models.ForeignKey(Employee, limit_choices_to={'manager': True}, on_delete=models.CASCADE)
    duration = models.CharField(max_length=200, help_text='Estimated Project End Duration')
    duration_unit = models.ForeignKey(DurationUnit, limit_choices_to={'active': True}, on_delete=models.CASCADE)
    employees = models.ManyToManyField(Employee, limit_choices_to={'manager': False}, related_name='employees')
    active = models.BooleanField(default=True)
