from datetime import timedelta, date, datetime, time
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django_userforeignkey.request import get_current_user

from employee.models import Employee
from settings.models import PublicHolidayDate


class LeaveMixin(models.Model):
    MEDICAL = "medical"
    HALF_DAY = "half_day"
    APPLIED_TIME_LIMIT = 18
    APPLIED_ERROR_MSG = (
        "You can not apply any leave application after 06:00 PM for tomorrow."
    )
    LEAVE_CHOICE = (
        ("casual", "Casual Leave"),
        ("medical", "Medical Leave"),
        ("non_paid", "Non Paid Leave"),
        ("half_day", "Half Day Casual"),
        ("half_day_medical", "Half Day Medical"),
        ("half_day_non_paid", "Half Day Non Paid"),
        ("emergency_leave", "Emergency Leave"),
        ("system_generated", "System Generated"),
    )
    LEAVE_STATUS = (
        ("pending", "⏳ Pending"),
        ("approved", "\u2705 Approved"),
        ("rejected", "⛔ Rejected"),
        ("need_discussion", "🤔 Need Discussion"),
    )

    start_date = models.DateField()
    end_date = models.DateField()
    total_leave = models.FloatField()
    note = models.TextField(null=True)
    leave_type = models.CharField(
        choices=LEAVE_CHOICE, max_length=20, verbose_name="Approved Leave Type"
    )
    applied_leave_type = models.CharField(
        choices=LEAVE_CHOICE, max_length=20, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default="pending")
    employee = models.ForeignKey(
        Employee, limit_choices_to={"active": True}, on_delete=models.CASCADE
    )

    def clean_fields(self, exclude=None):
        leave_type = self.applied_leave_type
        # print(leave_type)
        # print(self.leave_attachment.all())
        # Now you can use 'leave_type_value' as needed
        # ...

        user = get_current_user()
        # TODO : need to re-format
        if self.start_date is not None and self.end_date is not None:
            # if self.applied_leave_type == "casual":
            #     if self.start_date == date.today():
            #         raise ValidationError(
            #             "You have to apply casual leave before 1 day of start date"
            #         )
            #     if self.start_date < date.today():
            #         raise ValidationError(
            #             "You can not apply any leave past date. You have to apply for emergency or non paid leave"
            #         )
            #     if (
            #         (self.start_date - date.today()).days <= 1
            #         and time(self.APPLIED_TIME_LIMIT, 0) < datetime.now().time()
            #         and not user.has_perm("employee.can_add_leave_at_any_time")
            #     ):
            #         raise ValidationError({"start_date": self.APPLIED_ERROR_MSG})
            # if self.has_emergency_leave_last_3_months():
            #     raise ValidationError(
            #         "You can not apply emergency leave more than 1 in last 3 months"
            #     )
            from django.contrib.auth.models import Group

            # difference = self.end_date - self.start_date
            # print(difference >= timedelta(days=3))
            # if difference >= timedelta(days=3) and self.leave_type == "casual":
            #     submission_time = date.today()
            #     submission_difference = self.start_date - submission_time
            #     print(submission_difference)
            #     if submission_difference < timedelta(days=7):
            #         raise ValidationError(
            #             {
            #                 "start_date": "For consecutive 3 or more days of casual leave, you have to apply at least 7 days before the leave"
            #             }
            #         )

            # try:
            #     group = Group.objects.get(name="HR-Operation")
            # except Group.DoesNotExist:
            #     Group.objects.create(name="HR-Operation")
            print(self.start_date)
            print(date.today())
            print((self.start_date - date.today()).seconds)
            print((self.start_date - date.today()).days)
            # if self.leave_type not in [self.MEDICAL, self.HALF_DAY]:
            #     if (self.start_date - date.today()).days == 1 and time(self.APPLIED_TIME_LIMIT, 0) < datetime.now().time() and not user.has_perm('employee.can_add_leave_at_any_time'):
            #         raise ValidationError(
            #             {
            #                 "start_date": self.APPLIED_ERROR_MSG
            #             }
            #         )
            #     elif (self.start_date - date.today()).days < 1 and not user.has_perm('employee.can_add_leave_at_any_time'):
            #         raise ValidationError(
            #             {
            #                 "start_date": "You can not apply leave for past."
            #             }
            #         )

            if self.start_date > self.end_date:
                raise ValidationError(
                    {
                        "end_date": "End date must be greater then or equal {}".format(
                            self.start_date
                        )
                    }
                )
            return super().clean_fields(exclude=exclude)

    def save(self, *args, **kwargs):
        office_holidays = PublicHolidayDate.objects.filter(
            date__gte=self.start_date, date__lte=self.end_date
        ).values_list("date", flat=True)
        print(office_holidays)
        delta, weekly_holiday, public_holiday = self.end_date - self.start_date, [], []
        self.note = ""
        for i in range(delta.days + 1):
            date = self.start_date + timedelta(days=i)
            if date.strftime("%A") in ["Saturday", "Sunday"]:
                self.note += "The date {} is weekly holiday \n".format(date)
                weekly_holiday.append(date)
            if date in office_holidays:
                self.note += "The date {} is public holiday \n".format(date)
                public_holiday.append(date)
        print("employee", self.leave_type == "non_paid")
        if self.leave_type != "non_paid":
            self.total_leave = (delta.days + 1) - (
                len(weekly_holiday) + len(public_holiday)
            )
            self.note += "Applied day total {}. chargeable day {}".format(
                delta.days + 1, self.total_leave
            )
        else:
            self.total_leave = delta.days + 1
            self.note = "Applied day total {}. chargeable day {}".format(
                delta.days + 1, self.total_leave
            )

        # if self.employee.permanent_date is None:
        #     self.leave_type = 'non_paid'

        super().save(*args, **kwargs)

    class Meta:
        abstract = True
