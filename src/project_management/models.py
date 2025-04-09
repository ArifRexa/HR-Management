from ast import mod
from datetime import datetime
import datetime
from datetime import timedelta
from typing import Iterable
from dateutil.relativedelta import relativedelta, FR
from uuid import uuid4

from django.utils import timezone
from datetime import date
from dateutil.utils import today
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, ExpressionWrapper, Case, Value, When, F, Q
from django.db.models.functions import Trunc, ExtractWeekDay, ExtractWeek
from django.db.models.signals import pre_save
from django.db.models.signals import post_save

from django.dispatch import receiver
from tinymce.models import HTMLField
from config.model.TimeStampMixin import TimeStampMixin
from config.model.AuthorMixin import AuthorMixin
from employee.models import Employee
from django.utils.html import format_html
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from icecream import ic

# from employee.models import LeaveManagement
from django.apps import apps

from website.models_v2.industries_we_serve import IndustryServe, ServeCategory
from website.models_v2.services import ServicePage


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


class ClientReview(TimeStampMixin):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class PaymentMethod(TimeStampMixin):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class InvoiceType(TimeStampMixin):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Country(TimeStampMixin):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ClientStatus(models.IntegerChoices):
    FOLLOW_UP = 1, "Follow Up"
    MEETING = 2, "Meeting"


class CurrencyType(TimeStampMixin):
    currency_name = models.CharField(max_length=200, help_text="Example: US Dollar, Euro, etc.", blank=True, null=True)
    currency_code = models.CharField(max_length=10, help_text="Example: USD, EUR, etc.", blank=True, null=True)
    icon = models.CharField(max_length=10, help_text="Currency symbol like $, €, £", blank=False, null=False)
    is_active = models.BooleanField(default=True, help_text="Set as active currency")
    is_default = models.BooleanField(default=False, help_text="Set as default currency")
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Exchange rate relative to base currency"
    )

    # def save_model(self, request, obj, form, change):
    #     try:
    #         super().save_model(request, obj, form, change)
    #         if obj.is_default:
    #             return 1
    #             # self.messages(request, f"{obj.currency_name} has been set as the default currency.")
    #     except Exception as e:
    #         self.message_user(request, str(e))

    def save(self, *args, **kwargs):
        is_new_default = False
        if self.pk:
            old_instance = CurrencyType.objects.get(pk=self.pk)
            is_new_default = not old_instance.is_default and self.is_default

        # If this currency is being set as default
        if self.is_default:
            # Set all other currencies' is_default to False
            CurrencyType.objects.all().update(is_default=False)

        # If there are no currencies yet, make this one default
        if not self.pk and not CurrencyType.objects.exists():
            self.is_default = True
            is_new_default = True

        super().save(*args, **kwargs)

        # If no default currency exists after save, make this one default
        if not CurrencyType.objects.filter(is_default=True).exists():
            self.is_default = True
            super().save(*args, **kwargs)
            is_new_default = True

        # Update all clients if this became the new default
        if is_new_default:
            self.update_clients_currency()

    def update_clients_currency(self):
        """Update all clients to use this currency if it's the default"""
        if self.is_default:
            from .models import Client  # Import here to avoid circular import
            Client.objects.filter(currency__isnull=True).update(currency=self)
            # Or to update ALL clients:
            # Client.objects.all().update(currency=self)

    # def save(self, *args, **kwargs):
    #     # If this currency is being set as default
    #     if self.is_default:
    #         # Set all other currencies' is_default to False
    #         CurrencyType.objects.all().update(is_default=False)
    #
    #     # If there are no currencies yet, make this one default
    #     if not self.pk and not CurrencyType.objects.exists():
    #         self.is_default = True
    #
    #     super().save(*args, **kwargs)
    #
    #     # If no default currency exists after save, make this one default
    #     if not CurrencyType.objects.filter(is_default=True).exists():
    #         self.is_default = True
    #         super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # If this is the first currency being created, make it default
    #     if not self.pk and not CurrencyType.objects.exists():
    #         self.is_default = True
    #         self.currency_name = "US Dollar"
    #         self.currency_code = "USD"
    #         self.icon = "$"
    #
    #     # If this currency is being set as default, unset other defaults
    #     if self.is_default:
    #         CurrencyType.objects.filter(is_default=True).update(is_default=False)
    #
    #     super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_default:
            raise ValueError("Cannot delete the default currency")
        super().delete(*args, **kwargs)

    # @classmethod
    # def get_default_currency(cls):
    #     # First try to get the default currency
    #     default_currency = cls.objects.filter(is_default=True).first()
    #     if default_currency:
    #         return default_currency
    #
    #     # If no default currency exists, get or create USD
    #     return cls.objects.get_or_create(
    #         currency_code="USD",
    #         defaults={
    #             'currency_name': "US Dollar",
    #             'icon': "$",
    #             'is_default': True,
    #             'is_active': True,
    #         }
    #     )[0]

    @classmethod
    def get_default_currency_id(cls):
        currency = cls.objects.filter(is_default=True).first()
        if currency:
            return currency.id
        return None

    def __str__(self):
        return f"{self.icon} {self.currency_name} ({self.currency_code})"

    class Meta:
        verbose_name = "Currency Type"
        verbose_name_plural = "Currency Types"


class Client(TimeStampMixin, AuthorMixin):
    name = models.CharField(max_length=200)
    web_name = models.CharField(
        max_length=200, verbose_name="Web Name", null=True, blank=True
    )
    active = models.BooleanField(default=True)
    designation = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=80, null=True, blank=True)
    invoice_cc_email = models.TextField(
        null=True, blank=True, help_text="Comma-separated email addresses for CC"
    )
    bill_from = models.TextField(null=True, blank=True)
    # cc_email = models.TextField(
    #     null=True, blank=True, help_text="Comma-separated email addresses for CC"
    # )
    address = models.TextField(null=True, blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True
    )
    logo = models.ImageField(null=True, blank=True, verbose_name="Company Logo")
    is_need_feedback = models.BooleanField(default=False, verbose_name="Need Feedback")
    # show_in_web = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    client_feedback = HTMLField(null=True, blank=True)
    image = models.ImageField(
        upload_to="client_images", null=True, blank=True, verbose_name="Client Image"
    )
    linkedin_url = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    is_hour_breakdown = models.BooleanField(default=False)
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name="clients",
    )
    invoice_type = models.ForeignKey(
        InvoiceType,
        on_delete=models.SET_NULL,
        null=True,
    )
    review = models.ManyToManyField(
        ClientReview, blank=True, verbose_name="Client Review", related_name="clients"
    )
    currency = models.ForeignKey(
        CurrencyType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clients'
    )
    hourly_rate = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    active_from = models.DateField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        choices=ClientStatus.choices,
        null=True,
        blank=True,
    )
    follow_up_date = models.DateField(null=True, blank=True)
    meeting_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def is_active_over_six_months(self):
        if not self.active_from:
            return False
        return timezone.now().date() >= self.active_from + timedelta(days=180)


class ClientExperience(Client):
    class Meta:
        proxy = True
        verbose_name = "CX"
        verbose_name_plural = "CX"

    def __str__(self):
        return self.name


class ClientAttachment(models.Model):
    clients = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=200, null=True)
    attachment = models.FileField(upload_to="client_attachments/")

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"


class ClientInvoiceDate(models.Model):
    clients = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True, blank=True
    )
    invoice_date = models.DateField(null=True, blank=True)


class ProjectOverview(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=100)
    description = HTMLField()
    img = models.ImageField()

    def __str__(self):
        return self.title


class ProjectStatement(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=100)
    description = HTMLField()
    img = models.ImageField()

    def __str__(self):
        return self.title


class ProjectChallenges(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=100)
    description = HTMLField()
    img = models.ImageField()

    def __str__(self):
        return self.title


class ProjectSolution(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=100)
    description = HTMLField()
    img = models.ImageField()

    def __str__(self):
        return self.title


from django.db import models


class ProjectResults(models.Model):
    title = models.CharField(max_length=200)
    increased_sales = models.CharField(max_length=20)
    return_on_investment = models.CharField(max_length=10)
    increased_order_rate = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class ProjectPlatform(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class ProjectIndustry(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class ProjectService(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


# Create your models here.
class Project(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=200)
    web_title = models.CharField(
        max_length=200, verbose_name="Web Title", null=True, blank=True
    )
    slug = models.SlugField(null=True, blank=True, unique=True)
    description = models.TextField(verbose_name="Sub Title")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    client_web_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Client Web Name"
    )
    client_image = models.ImageField(
        upload_to="client_images",
        null=True,
        blank=True,
        verbose_name="Client Web Image",
    )
    client_review = models.TextField(null=True, blank=True)
    platforms = models.ManyToManyField(
        ProjectPlatform, related_name="projects", blank=True
    )
    industries = models.ForeignKey(
        "website.IndustryWeServe",
        related_name="projects",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    services = models.ForeignKey(
        ServicePage,
        related_name="projects",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    live_link = models.URLField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True
    )
    active = models.BooleanField(default=True)
    is_special = models.BooleanField(default=False)
    in_active_at = models.DateField(null=True, blank=True)
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    activate_from = models.DateField(null=True, blank=True)
    featured_image = models.ImageField(
        null=True, blank=True, verbose_name="Banner Image"
    )
    display_image = models.ImageField(
        null=True, blank=True, upload_to="project/display_image"
    )
    project_logo = models.ImageField(upload_to="project_logo", null=True, blank=True)
    special_image = models.ImageField(upload_to="special_image", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="project_thumbnails", null=True, blank=True)
    featured_video = models.URLField(null=True, blank=True)
    show_in_website = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="projects")
    identifier = models.CharField(
        max_length=50,
        default=uuid4,
    )
    is_highlighted = models.BooleanField(verbose_name="Is Highlighted?", default=False)
    is_team = models.BooleanField(verbose_name="Is Team?", default=False)
    # case_study_pdf = models.FileField(
    #     verbose_name="Case Study File (PDF)",
    #     help_text="Only Upload PDF File",
    #     upload_to="case_study_pdf", 
    #     null=True, 
    #     blank=True, 
    #     validators=[
    #         FileExtensionValidator(
    #             allowed_extensions=["pdf"], 
    #             message="Only PDF files are allowed. Please upload a valid PDF file."
    #         )
    #     ]
    # )

    # project_results = models.OneToOneField(
    #     ProjectResults,
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="project",
    # )

    # location_image = models.ImageField(null=True, blank=True)
    # service_we_provide_image = models.ImageField(null=True, blank=True)
    # industry_image = models.ImageField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.title[:51])
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["title"]
        permissions = [
            (
                "can_see_all_project_field",
                "Can See All Project Field",
            ),
            (
                "can_see_hourly_rate",
                "Can See Hourly Rate",
            ),
        ]

    def clean(self):
        super().clean()

        # if self.hourly_rate is not None and self.activate_from is None:
        #     raise ValidationError(
        #         "If hourly rate is provided, activate from is mandatory."
        #     )
        # if self.activate_from is not None and self.hourly_rate is None:
        #     raise ValidationError(
        #         "If activate from is provided, hourly rate is mandatory."
        #     )

    def __str__(self):
        client_name = self.client.name if self.client else "No Client"
        return f"{self.title} ({client_name})"

    def durations(self):
        duration = datetime.datetime.now() - self.created_at
        return duration.days

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

    # def last_n_months_feedback(self, num_of_months):
    #     end_date = timezone.now().date()
    #     start_date = end_date - relativedelta(months=num_of_months)
    #
    #
    #     return ClientFeedback.objects.filter(
    #         project=self,
    #         feedback_month__range=[start_date, end_date]
    #     ).order_by('feedback_month')
    def last_n_months_feedback(self, num_of_months):
        end_date = timezone.now().date()
        start_date = end_date - relativedelta(months=num_of_months)

        return (
            self.clientfeedback_set.filter(
                feedback_month__lte=end_date,
                feedback_month__gt=start_date,
            )
            .order_by("feedback_month")
            .exclude(project__active=False)
        )

    @property
    def check_is_weekly_project_hour_generated(self):
        latest_project_hour = (
            ProjectHour.objects.filter(project=self).order_by("created_at").last()
        )
        if latest_project_hour:
            latest_project_hour_date = latest_project_hour.created_at.date()
            # print(f"latest_project_hour_date: {latest_project_hour_date}")
            today = timezone.now().date()
            # print(f"today: {today}")
            last_friday = today - timedelta(days=(today.weekday() + 3) % 7)
            # print(f"last_friday: {last_friday}")
            if latest_project_hour_date < last_friday and today.weekday() in [
                4,
                5,
                6,
                0,
            ]:
                return False  # RED
            else:
                return True  # BLACK
        else:
            return True  # BLACK

    @property
    def associated_employees(self):
        return Employee.objects.filter(
            employeeproject__project=self, employeeproject__project__active=True
        )


class ProjectResultStatistic(TimeStampMixin):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_results", null=True
    )
    title = models.CharField(max_length=255)
    result = models.CharField(max_length=20)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Project Result"
        verbose_name_plural = "Project Results"


class PlatformImage(TimeStampMixin):
    image = models.ImageField(null=True, blank=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )


class ProjectServiceSolution(TimeStampMixin):
    project = models.ForeignKey(
        Project,
        related_name="service_solutions",
        on_delete=models.SET_NULL,
        null=True,
    )
    title = models.CharField(max_length=255)
    short_description = models.TextField()
    description = HTMLField()


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
        return f"{self.project.title} - {str(self.token)[:-8]}"


class ProjectTechnology(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    technologies = models.ManyToManyField(Technology)

    def __str__(self):
        return self.title


class ProjectKeyPoint(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    icon = models.ImageField(null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title


class OurTechnology(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=200)
    technologies = models.ManyToManyField(Technology)


class ProjectScreenshot(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    image = models.ImageField()


class ProjectContent(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True, blank=True)
    content = HTMLField(null=True, blank=True)
    image = models.ImageField(upload_to="project_images/", null=True, blank=True)
    image2 = models.ImageField(upload_to="project_images/", null=True, blank=True)

    def __str__(self):
        return self.title or "-"


class ProjectKeyFeature(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=300, null=True, blank=True)
    description = HTMLField()
    img = models.ImageField(
        verbose_name="Image", upload_to="projects/key_features/", null=True, blank=True
    )
    img2 = models.ImageField(upload_to="project_images/", null=True, blank=True)

    def __str__(self):
        return self.title or str(self.pk)


from django.core.validators import FileExtensionValidator


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
    STATUS_CHOICE = (("pending", "⌛ Pending"), ("approved", "✔ Approved"))

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
    tpm = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="project_hours",
        limit_choices_to={"active": True, "is_tpm": True},
        verbose_name="TPM",
    )
    # approved_by_cto = models.BooleanField(default=False)
    # operation_feedback = models.URLField(
    #     blank=True, null=True, verbose_name="Operation Feedback"
    # )
    # client_exp_feedback = models.URLField(
    #     blank=True, null=True, verbose_name="Client Experience Feedback"
    # )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending",
        verbose_name="TPM Approval Status",
    )
    report_file = models.FileField(
        upload_to="project_hours/",
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),
        ],
        verbose_name="Weekly Update (PDF)",
        help_text="Must Be You have to Give Report File"
    )

    def __str__(self):
        return f"{self.project} | {self.manager}"

    def clean(self):
        if (
            self.date is not None
            and self.date.weekday() != 4
            and self.hour_type != "bonus"
        ):
            raise ValidationError({"date": "Today is not Friday"})
        if not self.project:
            raise ValidationError({"project": "You have to must assign any project"})

    def save(self, *args, **kwargs):
        # if not self.manager.manager:
        #     self.payable = False

        if self.pk:
            old_instance = ProjectHour.objects.get(id=self.id)
            if old_instance.hours != self.hours:
                ProjectHourHistry.objects.create(
                    date=self.date, history=self, hour_history=self.hours
                )
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


@receiver(post_save, sender=ProjectHour)
def create_project_hour_history(sender, instance, created, **kwargs):
    if created:  # Only run if a new ProjectHour is created
        ProjectHourHistry.objects.create(
            date=instance.date, history=instance, hour_history=instance.hours
        )


class ProjectHourHistry(models.Model):
    date = models.DateField()
    history = models.ForeignKey(
        ProjectHour, on_delete=models.CASCADE, null=True, blank=True
    )
    hour_history = models.FloatField(null=True, blank=True)


class EmployeeProjectHour(TimeStampMixin, AuthorMixin):
    project_hour = models.ForeignKey(ProjectHour, on_delete=models.CASCADE)
    hours = models.FloatField()
    employee = models.ForeignKey(
        Employee,
        on_delete=models.RESTRICT,
        limit_choices_to={"active": True, "project_eligibility": True},
    )
    # update_data = models.TextField(blank=True, null=True, verbose_name="Update")

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
    created_at = models.DateTimeField(default=timezone.now)
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
    update = models.TextField(
        null=True,
        blank=True,
        default=" ",
        help_text="This will go to the client, so please ensure no unnecessary information is included",
    )
    updates_json = models.JSONField(
        null=True, blank=True, verbose_name="Update For Client"
    )
    management_updates = models.TextField(
        null=True,
        blank=True,
        verbose_name="Note",
        help_text="You can add any additional links or notes that help the DevLead/TPM understand your daily update",
    )

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
            (
                "can_approve_or_edit_daily_update_at_any_time",
                "Can approve or update daily project update at any time",
            ),
            (
                "can_submit_previous_daily_project_update",
                "Can Submit Previous Daily Project Update",
            ),
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
            return "\n".join([f"{i[0]}" for i in self.updates_json])
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


class DailyProjectUpdateGroupByClient(DailyProjectUpdate):
    class Meta:
        proxy = True
        permissions = [
            ("see_all_employee_update", "Can see all daily update"),
        ]
        verbose_name = "Group By Client"
        verbose_name_plural = "Group By Client"

    def __str__(self) -> str:
        return self.project.client.name


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


# class ClientFeedback(AuthorMixin, TimeStampMixin):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#
#     feedback_week = models.DateField(null=True)
#
#     feedback = models.TextField()
#     avg_rating = models.FloatField()
#
#     rating_communication = models.FloatField()
#     rating_output = models.FloatField()
#     rating_time_management = models.FloatField()
#     rating_billing = models.FloatField()
#     rating_long_term_interest = models.FloatField()
#
#     @property
#     def has_red_rating(self):
#         red_line = 3.5
#
#         return (
#             self.rating_communication <= red_line
#             or self.rating_output <= red_line
#             or self.rating_time_management <= red_line
#             or self.rating_billing <= red_line
#             or self.rating_long_term_interest <= red_line
#         )
#
#     class Meta:
#         permissions = (
#             ("can_see_client_feedback_admin", "Can see Client Feedback admin"),
#         )
#
#     def save(self, *args, **kwargs):
#         avg_rating = (
#             self.rating_communication
#             + self.rating_output
#             + self.rating_time_management
#             + self.rating_billing
#             + self.rating_long_term_interest
#         )
#         avg_rating = round(avg_rating / 5, 1)
#         self.avg_rating = avg_rating
#         super(ClientFeedback, self).save(*args, **kwargs)
#         self.feedback_week = self.created_at + relativedelta(weekday=FR(-1))
#         return super(ClientFeedback, self).save(*args, **kwargs)
#
#     def __str__(self) -> str:
#         return f"{self.project.title} ({str(self.avg_rating)})"
class ClientFeedback(AuthorMixin, TimeStampMixin):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # feedback_week = models.DateField(null=True)
    feedback_month = models.DateField(null=True)
    feedback = models.TextField()
    avg_rating = models.FloatField()

    rating_overall_satisfaction = models.FloatField(blank=True, null=True)
    rating_communication = models.FloatField(blank=True, null=True)
    rating_quality_of_work = models.FloatField(blank=True, null=True)
    rating_time_management = models.FloatField(blank=True, null=True)
    rating_understanding_of_requirements = models.FloatField(blank=True, null=True)
    rating_value_for_money = models.FloatField(blank=True, null=True)
    rating_recommendations = models.FloatField(blank=True, null=True)

    @property
    def has_red_rating(self):
        red_line = 3.5
        return (
            self.rating_communication is not None
            and self.rating_communication <= red_line
            or self.rating_overall_satisfaction is not None
            and self.rating_overall_satisfaction <= red_line
            or self.rating_quality_of_work is not None
            and self.rating_quality_of_work <= red_line
            or self.rating_time_management is not None
            and self.rating_time_management <= red_line
            or self.rating_value_for_money is not None
            and self.rating_value_for_money <= red_line
            or self.rating_understanding_of_requirements is not None
            and self.rating_understanding_of_requirements <= red_line
            or self.rating_recommendations is not None
            and self.rating_recommendations <= red_line
        )

    class Meta:
        permissions = (
            ("can_see_client_feedback_admin", "Can see Client Feedback admin"),
        )

    def save(self, *args, **kwargs):
        # Calculate average rating based on available ratings
        ratings = [
            self.rating_communication,
            self.rating_overall_satisfaction,
            self.rating_quality_of_work,
            self.rating_time_management,
            self.rating_value_for_money,
            self.rating_understanding_of_requirements,
            self.rating_recommendations,
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if valid_ratings:
            avg_rating = round(sum(valid_ratings) / len(valid_ratings), 1)
        else:
            avg_rating = None  # Handle cases where no ratings are provided

        self.avg_rating = avg_rating
        super(ClientFeedback, self).save(*args, **kwargs)
        # self.feedback_week = self.created_at + relativedelta(weekday=FR(-1))
        self.feedback_month = timezone.now().date().replace(day=1)
        return super(ClientFeedback, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.project.title} ({str(self.avg_rating)})"

    @staticmethod
    def get_current_month():
        return timezone.now().date().replace(day=1)

    @staticmethod
    def get_last_two_months():
        today = timezone.now().date()
        current_month = today.replace(day=1)
        last_month = (current_month - relativedelta(months=1)).replace(day=1)
        two_months_ago = (current_month - relativedelta(months=2)).replace(day=1)
        return [current_month, last_month, two_months_ago]

    @staticmethod
    def get_feedback_for_recent_months():
        current_month, last_month, two_months_ago = ClientFeedback.get_last_two_months()
        return ClientFeedback.objects.filter(
            feedback_month__in=[current_month, last_month, two_months_ago]
        )


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
        ("sqa", "SQA"),
    )
    name = models.CharField(max_length=255, null=True)
    project = models.ForeignKey(
        Project,
        related_name="project_reports",
        limit_choices_to={"active": True},
        on_delete=models.CASCADE,
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICE, default="manager")
    send_to = models.CharField(verbose_name="Send To", max_length=255)
    api_token = models.TextField(verbose_name="API Token")

    class Meta:
        verbose_name = "Project Report"
        verbose_name_plural = "Project Reports"

    def __str__(self):
        return f"{self.project} update to {self.send_to}"

    class Meta:
        verbose_name = "Project Report"
        verbose_name_plural = "Project Reports"


class EnableDailyUpdateNow(AuthorMixin, TimeStampMixin):
    name = models.CharField(max_length=24)
    enableproject = models.BooleanField(default=False)
    last_time = models.TimeField(null=True, blank=True)

    def clean(self):
        if self.last_time is None:
            raise ValidationError("Please Enter Last Time")
        # Ensure only one object of this class exists
        # if not self.pk and EnableDailyUpdateNow.objects.exists():
        #     raise ValidationError("Only one instance of EnableDailyUpdateNow can be created. And One instance is already exist.")

    def save(self, *args, **kwargs):
        # Ensure only one object of this class exists
        # if not self.pk and EnableDailyUpdateNow.objects.exists():
        #     # If trying to create a new object and one already exists, raise an exception
        #     raise Exception("Only one instance of EnableDailyUpdateNow can be created.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if EnableDailyUpdateNow.objects.count() <= 1:
            raise ValidationError(
                "At least one instance of EnableDailyUpdateNow must remain in the database."
            )
        return super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Project Update Enable"
        verbose_name_plural = "Project Update Enable by me"
        # permissions = (("can_change_daily_update_any_time", "Can change daily Update any Time"),)


class ObservationProject(TimeStampMixin, AuthorMixin):
    project_name = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_projects",
    )

    class Meta:
        verbose_name = "Observe New Project"
        # verbose_name_plural = 'Observations'


@receiver(post_save, sender=Project)
def create_observation(sender, instance, created, **kwargs):
    if created:
        ObservationProject.objects.create(project_name=instance)


# @receiver(post_save, sender=ProjectHour)
# def create_income(sender, instance, created, **kwargs):
#     print("sssssssssssssssssssssss create income has called ssssssssssssssssssss")
#     from account.models import Income

#     if created and instance.hour_type == "project":
#         project = instance.project
#         if project:
#             Income.objects.create(
#                 project=project,
#                 hours=instance.hours,
#                 hour_rate=project.hourly_rate
#                 if project.hourly_rate is not None
#                 else 0.00,
#                 convert_rate=90.0,  # Default convert rate
#                 date=instance.date,
#                 status="pending",
#             )


class ClientFeedbackEmail(models.Model):
    Feedback_Type_Choices = [
        ("initial", "Initial Feedback"),
        ("reminder", "Reminder Feedback"),
    ]
    subject = models.CharField(max_length=255, null=True, blank=True)
    body = HTMLField()
    feedback_type = models.CharField(
        max_length=50, choices=Feedback_Type_Choices, default="initial"
    )
