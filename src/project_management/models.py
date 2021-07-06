from django.contrib.auth.models import User
from django.db import models

from config.model.TimeStampMixin import TimeStampMixin
from config.model.AuthorMixin import AuthorMixin
from employee.models import Employee


class Client(TimeStampMixin, AuthorMixin):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=80)
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

# TODO : Employee project hour
