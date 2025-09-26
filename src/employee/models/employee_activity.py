import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee
from project_management.models import Project


class EmployeeOnline(TimeStampMixin, AuthorMixin):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

    class Meta:
        permissions = (("can_see_all_break", "Can able to see all break"),)


@receiver(post_save, sender=EmployeeOnline)
def save_employee_attendance(sender, **kwargs):
    instance: EmployeeOnline = kwargs["instance"]
    # TODO : set data in employee attendance if it's first attempt of active
    attendance, created = EmployeeAttendance.objects.get_or_create(
        employee=instance.employee,
        date=timezone.now().date(),
        defaults={
            "date": timezone.now().date(),
            "entry_time": instance.created_at.time(),
        },
    )
    if instance.active:
        activity = EmployeeActivity.objects.filter(
            employee_attendance=attendance, end_time__isnull=True
        ).last()
        if not activity:
            EmployeeActivity.objects.create(
                employee_attendance=attendance,
                start_time=datetime.datetime.now(),
            )
    else:
        activities = EmployeeActivity.objects.filter(
            employee_attendance=attendance, end_time__isnull=True
        )
        if activities.exists():
            activities.update(end_time=timezone.now())


class EmployeeAttendance(TimeStampMixin, AuthorMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    entry_time = models.TimeField(default=timezone.now)
    exit_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    class Meta:
        verbose_name = "Employee Attendance"
        verbose_name_plural = "Employee Attendances"
        permissions = (
            ("can_see_full_month_attendance", "Can see full month attendance"),
            (
                "can_download_attendance_report",
                "Can download attendance report",
            ),
        )


class TrialEmployeeAttendance(EmployeeAttendance):
    class Meta:
        proxy = True


class EmployeeActivity(TimeStampMixin, AuthorMixin):
    employee_attendance = models.ForeignKey(
        EmployeeAttendance, on_delete=models.CASCADE
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    updated_by = UserForeignKey(
        auto_user=True,
        verbose_name="Updated By",
        related_name="activities_updated",
    )
    is_updated_by_bot = models.BooleanField(default=False)


class EmployeeProject(TimeStampMixin, AuthorMixin):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    project = models.ManyToManyField(
        Project, limit_choices_to={"active": True}, blank=True
    )

    @property
    def active_projects(self):
        return self.project.filter(active=True)

    # def __str__(self):
    #     return ', '.join([project.title for project in self.project.all()])
    def __str__(self):
        return "\n".join(project.title for project in self.project.all())
