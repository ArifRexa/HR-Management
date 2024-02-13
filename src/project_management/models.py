import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta, FR
from uuid import uuid4
from datetime import datetime

from dateutil.utils import today
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, ExpressionWrapper, Case, Value, When, F, Q
from django.db.models.functions import Trunc, ExtractWeekDay, ExtractWeek
from django.db.models.signals import pre_save
from django.dispatch import receiver
from tinymce.models import HTMLField

from config.model.TimeStampMixin import TimeStampMixin
from config.model.AuthorMixin import AuthorMixin
from employee.models import Employee
from django.utils.html import format_html
from icecream import ic
# from employee.models import LeaveManagement
from django.apps import apps

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
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True, blank=True
    )
    active = models.BooleanField(default=True)
    in_active_at = models.DateField(null=True, blank=True)
    emergency_operation = models.BooleanField(default=False)
    thumbnail = models.ImageField(null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    show_in_website = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)
    identifier = models.CharField(
        max_length=50,
        default=uuid4
    )
    on_boarded_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"active": True},
    )
    is_team = models.BooleanField(verbose_name="Is Team?", default=False)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def durations(self):
        duration = datetime.now() - self.created_at
        return duration.days

    def colorize(self):
        if self.emergency_operation:
            return "text-danger"
        elif self.durations() <= 28:
            return "text-primary"
        return ""

    @property
    def created_at_timestamp(self):
        return int(self.created_at.strftime("%s")) * 1000

    def set_project_hours(self, value):
        self.total_project_hours = value

    def last_x_weeks_feedback(self, x):
        today = datetime.datetime.today()
        last_xth_friday = datetime.datetime.today() + relativedelta(weekday=FR(-x))

        return (
            self.clientfeedback_set.filter(
                created_at__date__lte=today,
                created_at__date__gt=last_xth_friday,
            )
            .order_by("-created_at")
            .exclude(project__active=False)
        )


class ProjectDocument(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=220)
    extra_note = models.TextField(null=True, blank=True)
    document = models.FileField(
        upload_to="uploads/project_documents/%y/%m",
    )


class ProjectToken(TimeStampMixin, AuthorMixin):
    project = models.OneToOneField(
        Project, limit_choices_to={"active": True}, on_delete=models.CASCADE
    )
    token = models.CharField(default=uuid4, max_length=255)

    def __str__(self) -> str:
        return f"{self.project.title} - {self.token[:-8]}"


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
    FORCAST_SELECTOR = (
        ("increase", "✔ Increase"),
        ("decrease", "⌛ Decrease"),
        ("same", "⌛ Same"),
        ("confused", "😕 Confused"),
    )
    HOUR_TYPE_SELECTOR = (
        ("project", "Project Hour"),
        ("bonus", "Bonus Project Hour"),
    )

    manager = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        limit_choices_to=(Q(active=True) & (Q(manager=True) | Q(lead=True))),
    )

    hour_type = models.CharField(
        max_length=40,
        choices=HOUR_TYPE_SELECTOR,
        default="project",
        verbose_name="Project Hour Type",
    )
    project = models.ForeignKey(
        Project,
        limit_choices_to={"active": True},
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    date = models.DateField()
    hours = models.FloatField()
    description = models.TextField(blank=True, verbose_name="Explanation")
    forcast = models.CharField(
        max_length=40,
        choices=FORCAST_SELECTOR,
        verbose_name="Forecast next week hours",
        null=True,
        blank=True,
    )
    payable = models.BooleanField(default=True)
    approved_by_cto = models.BooleanField(default=False)
    cto_feedback = models.TextField(blank=True, null=True, verbose_name="Feedback")

    def __str__(self):
        return f"{self.project} | {self.manager}"

    def clean(self):
        if self.hours is None:
            raise ValidationError({"hours": f"Hours filed is required"})
        if (
                self.date is not None
                and self.date.weekday() != 4
                and self.hour_type != "bonus"
        ):
            raise ValidationError({"date": "Today is not Friday"})

    def save(self, *args, **kwargs):
        # if not self.manager.manager:
        #     self.payable = False
        super(ProjectHour, self).save(*args, **kwargs)

    def employee_hour(self, employee_id):
        total = self.employeeprojecthour_set.aggregate(Sum("hours"))
        return employee_id, total["hours__sum"]

    class Meta:
        verbose_name_plural = "Weekly Project Hours"
        permissions = [
            ("show_all_hours", "Can show all hours just like admin"),
            ("select_hour_type", "Can select Project Hour type"),
            ("weekly_project_hours_approve", "Can approved and give feedback from CTO"),
        ]


class EmployeeProjectHour(TimeStampMixin, AuthorMixin):
    project_hour = models.ForeignKey(ProjectHour, on_delete=models.CASCADE)
    hours = models.FloatField()
    employee = models.ForeignKey(
        Employee,
        on_delete=models.RESTRICT,
        limit_choices_to={"active": True},
    )

    class Meta:
        permissions = [
            ("change_recent_activity", "Can change if inserted recently (3days)"),
            ("see_all_employee_hour", "Can see all emploployee project hour"),
        ]
        verbose_name = "Employee Project Hour"
        verbose_name_plural = "Employee Project Hours"
        verbose_name = "Employee Project Hour"
        verbose_name_plural = "Employee Project Hours"


class EmployeeProjectHourGroupByEmployee(EmployeeProjectHour):
    class Meta:
        proxy = True

        verbose_name = "Weekly Employee Hours"
        verbose_name_plural = "Weekly Employee Hours"

    def __str__(self) -> str:
        return self.project_hour.project.title


class DailyProjectUpdate(TimeStampMixin, AuthorMixin):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.RESTRICT,
        limit_choices_to={"active": True},
        related_name="dailyprojectupdate_employee",
    )
    manager = models.ForeignKey(
        Employee,
        on_delete=models.RESTRICT,
        limit_choices_to=(Q(active=True) & (Q(manager=True) | Q(lead=True))),
        related_name="dailyprojectupdate_manager",
        help_text="Manager / Lead",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.RESTRICT,
        related_name="projects",
        limit_choices_to={"active": True},
    )
    hours = models.FloatField(default=0.0)
    # description = models.TextField(blank=True, verbose_name='Explanation')
    update = models.TextField(null=True, blank=True, default=' ')
    updates_json = models.JSONField(null=True, blank=True)

    STATUS_CHOICE = (
        ("pending", "⌛ Pending"),
        ("approved", "✔ Approved"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="pending")
    note = models.TextField(null=True, blank=True, help_text="Manager's note / remarks")

    # def clean(self):
    #     if self.hours < 4 and self.description == "":
    #         raise ValidationError({
    #             'description': f"Please explain why the hours is less than 4"
    #         })
    #     return super().clean()

    class Meta:
        permissions = [
            ("see_all_employee_update", "Can see all daily update"),
            ("can_approve_or_edit_daily_update_at_any_time", "Can approve or update daily project update at any time" ),
        ]
        verbose_name = "Daily Project Update"
        verbose_name_plural = "Daily Project Updates"


    @property
    def get_hours_history(self):
        historyData = ""
        if self.history is not None:
            for history in self.history.order_by("-created_at"):
                print(history)
                historyData += f"{history.hours}"
                if history != self.history.order_by("-created_at").last():
                    historyData += f" > "
            return format_html(historyData)

        return "No changes"

    @property
    def str_updates_json(self):
        # ic(self.updates_json)
        # out = '\n'.join([f"{i[0]} [{i[1]}]" for i in self.updates_json])
        # ic(out)
        if self.updates_json is not None:
            return '\n'.join([f"{i[0]} - {i[1]}H" for index, i in enumerate(self.updates_json)])
        # return '\n'.join(
        #     [f"{i[0]} - {i[1]}H {i[2] if (lambda lst, idx: True if idx < len(lst) else False)(i, 2) else ''} " for
        #      index, i in enumerate(self.updates_json)])
        else:
            return str(self.update)


    # def clean(self):
    #     # LeaveManagement = apps.get_model('employee', 'LeaveManagement')
    #     # if len(LeaveManagement.objects.filter(manager=self.manager, status='pending')) > 0:
    #     if len(self.employee.leave_management_manager.filter(status='pending')) > 0:
    #         raise ValidationError('You have pending leave application(s). Please approve first.')


class DailyProjectUpdateHistory(TimeStampMixin, AuthorMixin):
    daily_update = models.ForeignKey(
        DailyProjectUpdate, on_delete=models.CASCADE, related_name="history"
    )
    hours = models.FloatField(default=0.0)


class DailyProjectUpdateAttachment(TimeStampMixin, AuthorMixin):
    daily_update = models.ForeignKey(
        DailyProjectUpdate,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Daily Project Update",
    )
    title = models.CharField(max_length=220)
    attachment = models.FileField(
        verbose_name="Document",
        upload_to="uploads/daily_update/%y/%m",
        null=True,
        blank=True,
    )


class DailyProjectUpdateGroupByEmployee(DailyProjectUpdate):
    class Meta:
        proxy = True

        permissions = [
            ("see_all_employee_update", "Can see all daily update"),
        ]
        verbose_name = "Group By Employee"
        verbose_name_plural = "Group By Employee"

    def __str__(self) -> str:
        return self.project.title


class DailyProjectUpdateGroupByProject(DailyProjectUpdate):
    class Meta:
        proxy = True
        permissions = [
            ("see_all_employee_update", "Can see all daily update"),
        ]
        verbose_name = "Group By Project"
        verbose_name_plural = "Group By Project"

    def __str__(self) -> str:
        return self.project.title


class DailyProjectUpdateGroupByManager(DailyProjectUpdate):
    class Meta:
        proxy = True
        permissions = [
            ("see_all_employee_update", "Can see all daily update"),
        ]
        verbose_name = "Group By Manager"
        verbose_name_plural = "Group By Manager"

    def __str__(self) -> str:
        return self.project.title


class DurationUnit(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=200)
    duration_in_hour = models.FloatField(default=1)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ProjectResource(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(
        Project, limit_choices_to={"active": True}, on_delete=models.CASCADE
    )
    manager = models.ForeignKey(
        Employee,
        limit_choices_to={"manager": True, "active": True},
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(default=True)


class ProjectResourceEmployee(TimeStampMixin, AuthorMixin):
    project_resource = models.ForeignKey(
        ProjectResource, limit_choices_to={"active": True}, on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        Employee,
        limit_choices_to={
            "active": True,
            "manager": False,
            "employeeskill__isnull": False,
        },
        on_delete=models.CASCADE,
    )
    duration = models.FloatField(
        max_length=200, help_text="Estimated Project End Duration"
    )
    duration_unit = models.ForeignKey(
        DurationUnit, limit_choices_to={"active": True}, on_delete=models.CASCADE
    )
    duration_hour = models.FloatField()
    hour = models.FloatField(
        max_length=200,
        help_text="Estimated hours for each week",
        null=True,
        default=True,
    )

    def clean(self):
        if (
                ProjectResourceEmployee.objects.filter(employee=self.employee)
                        .exclude(id=self.id)
                        .first()
        ):
            raise ValidationError(
                {
                    "employee": f"{self.employee} is already been taken in another project"
                }
            )

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


class ClientFeedback(AuthorMixin, TimeStampMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    feedback_week = models.DateField(null=True)

    feedback = models.TextField()
    avg_rating = models.FloatField()

    rating_communication = models.FloatField()
    rating_output = models.FloatField()
    rating_time_management = models.FloatField()
    rating_billing = models.FloatField()
    rating_long_term_interest = models.FloatField()

    @property
    def has_red_rating(self):
        red_line = 3.5

        return (
                self.rating_communication <= red_line
                or self.rating_output <= red_line
                or self.rating_time_management <= red_line
                or self.rating_billing <= red_line
                or self.rating_long_term_interest <= red_line
        )

    class Meta:
        permissions = (
            ("can_see_client_feedback_admin", "Can see Client Feedback admin"),
        )

    def save(self, *args, **kwargs):
        avg_rating = (
                self.rating_communication
                + self.rating_output
                + self.rating_time_management
                + self.rating_billing
                + self.rating_long_term_interest
        )
        avg_rating = round(avg_rating / 5, 1)
        self.avg_rating = avg_rating
        super(ClientFeedback, self).save(*args, **kwargs)
        self.feedback_week = self.created_at + relativedelta(weekday=FR(-1))
        return super(ClientFeedback, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.project.title} ({str(self.avg_rating)})"


class CodeReview(TimeStampMixin, AuthorMixin):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, limit_choices_to={"active": True}
    )
    manager = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        limit_choices_to={"active": True, "manager": True},
        null=True,
        related_name="mange",
        blank=True,
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, limit_choices_to={"active": True}
    )

    naming_convention = models.FloatField()
    code_reusability = models.FloatField()
    oop_principal = models.FloatField()
    design_pattern = models.FloatField()
    standard_git_commit = models.FloatField()
    review_at = models.DateTimeField(auto_now_add=False, null=True)

    avg_rating = models.FloatField()

    comment = models.TextField()

    for_first_quarter = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        avg_rating = (
                self.naming_convention
                + self.code_reusability
                + self.oop_principal
                + self.design_pattern
                + self.standard_git_commit
        )
        avg_rating = round(avg_rating / 5, 1)
        self.avg_rating = avg_rating

        super(CodeReview, self).save(*args, **kwargs)

        if not self.created_at.date().day <= 15:
            self.for_first_quarter = False

        super(CodeReview, self).save(*args, **kwargs)

    class Meta:
        permissions = (("can_give_code_review", "Can give code review"),)


class CodeReviewEmployeeFeedback(TimeStampMixin, AuthorMixin):
    code_review = models.ForeignKey(CodeReview, on_delete=models.CASCADE)
    comment = models.TextField()


class ProjectReport(TimeStampMixin):
    TYPE_CHOICE = (
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("lead", "Lead"),
        ("sqa", "SQA")
    )
    name = models.CharField(max_length=255, null=True)
    project = models.ForeignKey(
        Project, related_name='project_reports',
        limit_choices_to={"active": True},
        on_delete=models.CASCADE
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICE, default="manager")
    send_to = models.CharField(
        verbose_name="Send To", max_length=255
    )
    api_token = models.TextField(verbose_name='API Token')

    class Meta:
        verbose_name = "Project Report"
        verbose_name_plural = "Project Reports"

    def __str__(self):
        return f"{self.project} update to {self.send_to}"

    class Meta:
        verbose_name = "Project Report"
        verbose_name_plural = "Project Reports"
