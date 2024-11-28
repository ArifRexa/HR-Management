from django.contrib.auth.models import User
from django.db import models
from tinymce import models as tinymce_models

# Create your models here.
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin


class FinancialYear(TimeStampMixin, AuthorMixin):
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)


class Designation(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class PayScale(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    basic = models.FloatField()
    travel_allowance = models.FloatField()
    house_allowance = models.FloatField()
    medical_allowance = models.FloatField()
    net_payable = models.FloatField()
    provision_period = models.IntegerField(help_text="Month")
    increment_period = models.IntegerField(help_text="increment month count")
    increment_rate = models.FloatField(help_text="In percentage")
    leave_in_cash_medical = models.FloatField(
        help_text="Medical Leave in cash, your submitted value will count as % percentage. "
        "It will automatically calculate to the employee salary sheet on year closing",
        verbose_name="Leave in Cash (Medical)",
        default=0.0,
    )
    leave_in_cash_casual = models.FloatField(
        help_text="Casual leave in cash, your submitted value will count as % percentage. "
        "It will automatically calculate to the employee salary sheet on year closing",
        verbose_name="Leave in Cash (Casual)",
        default=0.0,
    )

    def __str__(self):
        return self.title


class LeaveManagement(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    casual_leave = models.IntegerField()
    medical_leave = models.IntegerField()

    def __str__(self):
        return self.title


class PublicHoliday(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255)
    note = models.TextField(null=True)

    def __str__(self):
        return self.title


class PublicHolidayDate(TimeStampMixin):
    public_holiday = models.ForeignKey(
        PublicHoliday, on_delete=models.CASCADE, related_name="public_holiday"
    )
    date = models.DateField()


class Bank(TimeStampMixin, AuthorMixin):
    name = models.CharField(max_length=200)
    address = models.TextField(null=True, blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Letter(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=250)
    header = tinymce_models.HTMLField()
    sticky_header = models.BooleanField(default=False)
    body = tinymce_models.HTMLField()
    footer = tinymce_models.HTMLField()
    sticky_footer = models.BooleanField(default=False)


class OpenLetter(TimeStampMixin):
    title = models.CharField(max_length=255)
    message = models.TextField()


class Announcement(TimeStampMixin, AuthorMixin):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    rank = models.SmallIntegerField(default=0)

    description = tinymce_models.HTMLField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.description
    
    
class Notice(TimeStampMixin, AuthorMixin):
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)

    rank = models.SmallIntegerField(default=0)

    title = models.CharField(max_length=255)

    file = models.FileField(upload_to='notices/')


    def __str__(self):
        return self.title


# class FoodAllowanceExclusion(TimeStampMixin, AuthorMixin):
#     date = models.DateField()
#     number = models.IntegerField(help_text="Number of Food Allowance to be excluded")


# class EmployeeFoodAllowanceExclusion(TimeStampMixin, AuthorMixin):
#     foodallowance = models.ForeignKey(
#         to=FoodAllowanceExclusion,
#         on_delete=models.CASCADE,
#     )
#     employee = models.ForeignKey(
#         to="employee.Employee",
#         on_delete=models.CASCADE,
#         limit_choices_to={"active": True},
#     )
#     number = models.IntegerField()


class EmployeeFoodAllowance(TimeStampMixin, AuthorMixin):
    employee = models.ForeignKey(
        to="employee.Employee",
        on_delete=models.CASCADE,
        limit_choices_to={"active": True},
    )
    date = models.DateField()
    amount = models.IntegerField()

    class Meta:
        verbose_name = "Employee Food Allowance"
        verbose_name_plural = "Employee Food Allowances"

    def __str__(self) -> str:
        return f"{self.employee.full_name} | {self.amount} | {self.date.strftime('%B %d, %Y')}"


class EmailAnnouncement(TimeStampMixin, AuthorMixin):
    subject = models.TextField()
    body = tinymce_models.HTMLField(null=True, blank=True)


class EmailAnnouncementAttatchment(TimeStampMixin, AuthorMixin):
    email_announcement = models.ForeignKey(EmailAnnouncement, on_delete=models.CASCADE, null=True, blank=True)
    attachments = models.FileField(upload_to='email_attachments/', null=True, blank=True)

