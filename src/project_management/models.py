import datetime
from datetime import timedelta

from dateutil.utils import today
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from tinymce.models import HTMLField

from config.model.TimeStampMixin import TimeStampMixin
from config.model.AuthorMixin import AuthorMixin
from employee.models import Employee


class Technology(TimeStampMixin, AuthorMixin):
    icon = models.ImageField()
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Tag(TimeStampMixin, AuthorMixin):
    icon = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Client(TimeStampMixin, AuthorMixin):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=80)
    address = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=200)
    logo = models.ImageField(null=True, blank=True)
    show_in_web = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Create your models here.
class Project(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=200)
    slug = models.SlugField(null=True, blank=True, unique=True)
    description = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    in_active_at = models.DateField(null=True, blank=True)
    thumbnail = models.ImageField(null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    show_in_website = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)
    on_boarded_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                      limit_choices_to={'active': True})

    def __str__(self):
        return self.title

    @property
    def created_at_timestamp(self):
        return int(self.created_at.strftime("%s")) * 1000


class ProjectTechnology(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    technologies = models.ManyToManyField(Technology)

    def __str__(self):
        return self.title


class ProjectScreenshot(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    image = models.ImageField()


class ProjectContent(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = HTMLField()

    def __str__(self):
        return self.title


class ProjectHour(TimeStampMixin, AuthorMixin):
    manager = models.ForeignKey(Employee, limit_choices_to={'manager': True}, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, limit_choices_to={'active': True}, on_delete=models.SET_NULL, null=True,
                                blank=True)
    date = models.DateField()
    hours = models.FloatField()
    description = models.TextField(blank=True, verbose_name='Explanation')
    payable = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.project} | {self.manager}"

    def clean(self):
        if self.hours <= 25 and self.description == "":
            raise ValidationError({
                'description': f"Please explain why the hours is less then or equal 25"
            })

    def save(self, *args, **kwargs):
        if not self.manager.manager:
            self.payable = False
        super(ProjectHour, self).save(*args, **kwargs)

    def employee_hour(self, employee_id):
        total = self.employeeprojecthour_set.aggregate(Sum('hours'))
        return employee_id, total['hours__sum']

    class Meta:
        permissions = [
            ('show_all_hours', 'Can show all hours just like admin')
        ]


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
    duration_in_hour = models.FloatField(default=1)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ProjectResource(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, limit_choices_to={'active': True}, on_delete=models.CASCADE)
    manager = models.ForeignKey(Employee, limit_choices_to={'manager': True, 'active': True}, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class ProjectResourceEmployee(TimeStampMixin, AuthorMixin):
    project_resource = models.ForeignKey(ProjectResource, limit_choices_to={'active': True}, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee,
                                 limit_choices_to={'active': True, 'manager': False, 'employeeskill__isnull': False},
                                 on_delete=models.CASCADE)
    duration = models.FloatField(max_length=200, help_text='Estimated Project End Duration')
    duration_unit = models.ForeignKey(DurationUnit, limit_choices_to={'active': True}, on_delete=models.CASCADE)
    duration_hour = models.FloatField()
    hour = models.FloatField(max_length=200, help_text='Estimated hours for each week', null=True, default=True)

    def clean(self):
        if ProjectResourceEmployee.objects.filter(employee=self.employee).exclude(id=self.id).first():
            raise ValidationError({'employee': f'{self.employee} is already been taken in another project'})

    def save(self, *args, **kwargs):
        self.duration_hour = self.duration * self.duration_unit.duration_in_hour
        super().save(*args, **kwargs)

    @property
    def end_date(self):
        return self.updated_at + timedelta(hours=self.duration_hour)

    @property
    def endways(self):
        return self.end_date <= today() + timedelta(days=7)


class ProjectNeed(TimeStampMixin, AuthorMixin):
    technology = models.CharField(max_length=255)
    quantity = models.IntegerField()
    note = models.TextField(null=True, blank=True)
