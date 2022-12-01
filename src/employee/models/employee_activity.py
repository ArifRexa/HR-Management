import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee


class EmployeeOnline(TimeStampMixin, AuthorMixin):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("can_see_all_break", "Can able to see all break"),
        )


@receiver(post_save, sender=EmployeeOnline)
def save_employee_attendance(sender, **kwargs):
    instance = kwargs['instance']
    # TODO : set data in employee attendance if it's first attempt of active
    attendance, created = EmployeeAttendance.objects.get_or_create(
        employee=instance.employee,
        defaults={'date': datetime.datetime.today().date()}
    )
    print(attendance)
    print(instance.active)
    if instance.active:
        EmployeeActivity.objects.create(
            employee_attendance=attendance,
            start_time=datetime.datetime.now()
        )
        print('created employee activity')
    else:
        activity = EmployeeActivity.objects.filter(employee_attendance=attendance, end_time__isnull=True).first()
        if activity:
            activity.end_time = datetime.datetime.now()
            activity.save()
            print('completed employee activity')


class EmployeeAttendance(TimeStampMixin, AuthorMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    entry_time = models.TimeField(default=timezone.now)
    exit_time = models.TimeField(null=True, blank=True)


class EmployeeActivity(TimeStampMixin, AuthorMixin):
    employee_attendance = models.ForeignKey(EmployeeAttendance, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
