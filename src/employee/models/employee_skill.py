from django.db import models
from django.db.models import Q

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee
from django.core.validators import MaxValueValidator, MinValueValidator

class Skill(AuthorMixin, TimeStampMixin):
    title = models.CharField(unique=True, max_length=255)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class EmployeeSkill(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    percentage = models.FloatField(max_length=100)

    def __str__(self):
        return self.skill.title


class Learning(AuthorMixin, TimeStampMixin):
    asigned_to = models.ForeignKey(Employee,
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'project_eligibility': True, 'active': True},
                                   related_name='learning_to')
    asigned_by = models.ForeignKey(Employee,
                                   on_delete=models.CASCADE,
                                   limit_choices_to=(
                                           Q(active=True)
                                           & (
                                                   Q(manager=True)
                                                   | Q(lead=True)
                                           )
                                   ),
                                   related_name='learning_by')
    details = models.TextField(blank=False, null=True)

    def __str__(self):
        return self.asigned_to.full_name


class EmployeeTechnology(TimeStampMixin):
    name = models.CharField(max_length=255, unique=True)
    icon = models.ImageField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Employee Technology"
        verbose_name_plural = "Employee Technologies"
        ordering = ('name', '-created_at')

    def __str__(self):
        return self.name


class EmployeeExpertise(TimeStampMixin):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        limit_choices_to={'active': True}
    )

    class Meta:
        verbose_name = "Employee Expertise"
        verbose_name_plural = "Employee Expertises"
        ordering = ('-created_at', )

    def __str__(self):
        return f"{self.employee.full_name}'s Expertises"


class EmployeeExpertTech(TimeStampMixin):
    LEVEL_CHOICE = (
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('master', 'Master'),
    )
    employee_expertise = models.ForeignKey(
        EmployeeExpertise,
        on_delete=models.CASCADE,
        related_name='employee_expertise',
        null=True
    )
    technology = models.ForeignKey(EmployeeTechnology, limit_choices_to={'active': True}, on_delete=models.CASCADE)
    level = models.CharField(max_length=15, choices=LEVEL_CHOICE)
    percentage = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)], default=0)

    class Meta:
        verbose_name = "Employee Expert Tech"
        verbose_name_plural = "Employee Expert Techs"
        ordering = ('technology__name', )

    def __str__(self):
        return f"{self.technology.name} ({self.get_level_display()})"
