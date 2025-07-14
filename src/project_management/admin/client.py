from django import forms
from django.contrib import admin
from django.utils import timezone
from datetime import datetime
from django.contrib import messages as message
from django.db.models import (
    Case, DateField, When, Sum,
    F, functions, ExpressionWrapper, DurationField,
)
from django.http import HttpRequest
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _
from django.core.management import call_command
from django.db.models import Subquery, OuterRef, F, Sum, DecimalField, ExpressionWrapper, DurationField, functions
from django.db.models.functions import Coalesce# from networkx import project
from account.models import Income
from project_management.models import (
    Client,
    ClientAttachment,
    ClientExperience,
    ClientFeedbackEmail,
    ClientInvoiceDate,
    ClientReview,
    ClientStatus,
    Country,
    CurrencyType,
    InvoiceType,
    PaymentMethod,
    Project,
)
from django.db import models

class ClientInvoiceDateInline(admin.StackedInline):
    model = ClientInvoiceDate
    extra = 1


class ActiveProjectFilter(admin.SimpleListFilter):
    title = _("Active Project")
    parameter_name = "active_project"

    def lookups(self, request, model_admin):
        project_title = Project.objects.filter(active=True).values_list(
            "title", flat=True
        )
        return tuple((title, title) for title in project_title)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(project__title=self.value())
        return queryset


@admin.register(ClientReview)
class ClientReviewAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["review"]

    def has_module_permission(self, request: HttpRequest) -> bool:
        return False


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]

    def has_module_permission(self, request: HttpRequest) -> bool:
        return False


@admin.register(InvoiceType)
class InvoiceTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]

    def has_module_permission(self, request: HttpRequest) -> bool:
        return False


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]

    def has_module_permission(self, request: HttpRequest) -> bool:
        return False


class ClientAttachmentInline(admin.TabularInline):
    model = ClientAttachment
    extra = 1


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = (
            "name",
            # "web_name",
            "email",
            "invoice_cc_email",
            "designation",
            "company_name",
            "logo",
            "is_need_feedback",
            "client_feedback",
            "image",
            "linkedin_url",
            # "bill_from",
            # "cc_email",
            "address",
            "country",
            "notes",
            "is_hour_breakdown",
            "hourly_rate",
            "active_from",
            "payment_method",
            "invoice_type",
            "review",
        )

        widgets = {
            "invoice_cc_email": forms.Textarea(
                attrs={
                    "cols": 100,
                    "rows": 5,
                    "placeholder": "client1@gmail.com,client2@gmail.com",
                }
            ),
        }


@admin.register(CurrencyType)
class CurrencyTypeAdmin(admin.ModelAdmin):
    list_display = (
        "currency_name",
        "currency_code",
        "icon",
        "is_active",
        "is_default",
        "exchange_rate",
    )
    list_filter = ("is_active", "is_default")
    search_fields = ("currency_name", "currency_code")
    # readonly_fields = ('exchange_rate',)

    # def get_readonly_fields(self, request, obj=None):
    #     if obj and obj.is_default:
    #         return 'currency_name', 'currency_code', 'icon', 'is_default'
    #     return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of default currency
        if obj and obj.is_default:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "get_hourly_rate",
        "get_project_income",
        "get_inactive_from",
        "get_duration",
        "get_referrals_name",
        # "web_name",
        # "get_project_name",
        # "email",
        # 'hourly_rate_display',  # Add this
        # "linkedin_url",
        # "country",
        # "currency",
        "payment_method",
        "invoice_type",
        "get_remark",
        # "get_client_review",
    )
    fields = (
        "name",
        "hourly_rate",
        "inactive_from",
        "refered_by",
        "payment_method",
        "invoice_type",
        "remark",
        "email",
        "country",
        "review",
        "active",
        "invoice_cc_email",
        "designation",
        "company_name",
        "logo",
        # "is_need_feedback",
        # "client_feedback",
        "image",
        "linkedin_url",
        "bill_from",
        # "cc_email",
        "address",
        # "active_from",
        "notes",
        "is_hour_breakdown",
        "currency",
    )
    list_filter = [
        "is_need_feedback",
        "active",
        "review",
        "payment_method",
        "invoice_type",
        "currency",
    ]
    inlines = (ClientAttachmentInline, )
    search_fields = [
        "name",
        "web_name",
        "currency__currency_name",
        "currency__currency_code",
        "currency__icon",
    ]
    autocomplete_fields = ["country", "payment_method", "refered_by"]
    form = ClientForm
    actions = ["mark_as_in_active",]

    @admin.display(description="Project Name")
    def get_project_name(self, obj):
        project_name = obj.project_set.all().values_list("title", flat=True)
        return format_html("<br>".join(project_name))

    @admin.display(description="Inactive", ordering="inactive_from")
    def get_inactive_from(self, client_obj):
        return client_obj.inactive_from
    
    @admin.display(description="Referrals")
    def get_referrals_name(self, obj):
        client_referrals = Client.objects.filter(refered_by=obj).values_list("name", flat=True)
        return format_html("<br>".join(client_referrals))

    @admin.display(description="Hourly Rate", ordering="hourly_rate")
    def get_hourly_rate(self, obj):
        rate_display = "-"
        if obj.hourly_rate is not None:
            # Get currency icon
            currency_icon = obj.currency.icon if obj.currency else ""

            # Create the display string with icon
            rate_display = f"{currency_icon} {obj.hourly_rate}"

        html_template = get_template(
            "admin/project_management/list/client_info.html"
        )
        html_content = html_template.render(
            {
                "projects": obj.project_set.all(),
                "client_obj": obj,
                "rate_display": rate_display,
                "client_review": obj.review.all().values_list("name", flat=True),
            }
        )
        try:
            data = format_html(html_content)
        except:
            data = "-"    
        return data

    @admin.display(description="Age", ordering="created_at")
    def get_client_age(self, obj):
        return timesince(obj.created_at)

    @admin.display(description="Remark", ordering="remark")
    def get_remark(self, obj):
        if not obj.remark:
            return "-"
        html_template = get_template("admin/client_remark.html")

        html_content = html_template.render(
            {
                "remark": obj.remark,
            }
        )

        return mark_safe(html_content)

    def get_list_filter(self, request: HttpRequest):
        if request.user.has_perm("project_management.view_client"):
            return super().get_list_filter(request)
        self.list_filter.remove("payment_method")
        return self.list_filter

    @admin.action(description="Mark as In-active")
    def mark_as_in_active(self, request, queryset):
        try:
            queryset.update(active=False)
            self.message_user(
                request, "Selected clients are marked as active.", message.SUCCESS
            )
        except Exception:
            self.message_user(
                request, "Selected clients are not marked as active.", message.ERROR
            )
    
    # @admin.action(description="Set inactive-from value for inactive Clients.")
    # def set_inactive_from_value_for_inactive_alients(self, request, queryset):
    #     try:
    #         call_command("set_inactive_dates")
    #         self.message_user(
    #             request, "Inactive-from value set for Inactive Clients.", message.SUCCESS
    #         )
    #     except Exception:
    #         self.message_user(
    #             request, "Inactive-from value set failed for Inactive Clients!", message.ERROR
    #         )

    # get_project_name.short_description = "Project Name"
    # @admin.display(description="Client Review")
    # def get_client_review(self, obj):
    #     client_review = obj.review.all().values_list("name", flat=True)

    #     return format_html("<br>".join(client_review))


    # @admin.display(description="Income")
    # def get_project_income(self, client_object):
    #     client_project_ids = client_object.project_set.all().values_list("id", flat=True)
    #     total_income = 0.0
    #     for client_project_id in client_project_ids:
    #         total_income += Income.objects.filter(
    #             project_id=client_project_id,
    #             status="approved",
    #         ).annotate(
    #             sub_total=F("hours")*F("hour_rate")
    #         ).aggregate(
    #             total=Sum("sub_total")
    #         ).get("total") or 0.0
    #     return f"$ {total_income}"
    @admin.display(description="Income", ordering="total_income")
    def get_project_income(self, client_object):
        total_income = getattr(client_object, "total_income", None)
        if total_income is None:
            client_project_ids = client_object.project_set.all().values_list("id", flat=True)
            total_income = 0.0
            for client_project_id in client_project_ids:
                total_income += (
                    Income.objects.filter(project_id=client_project_id, status="approved")
                    .annotate(sub_total=F("hours") * F("hour_rate"))
                    .aggregate(total=Sum("sub_total"))
                    .get("total") or 0.0
                )
        return f"$ {float(total_income):.2f}"
    
    @admin.display(description="Duration", ordering="duration_in_days")
    def get_duration(self, client_object):
        """
        get active duration, Example: "1y 5m 10d"
        """
        current_date = timezone.now().date()

        active_from = client_object.active_from or current_date
        inactive_from = client_object.inactive_from or current_date

        total_days = (inactive_from - active_from).days
        years, remainder = divmod(total_days, 365)
        months, days = divmod(remainder, 30)

        time_list = []
        if years:
            time_list.append(f"{years}y")
        if months:
            time_list.append(f"{months}m")
        if days:
            time_list.append(f"{days}d")
        return " ".join(time_list) or None
    
    def has_module_permission(self, request):
        return False
    

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     current_date = timezone.now().date()

    #     active_from = F("active_from")
    #     inactive_from = F("inactive_from")
    #     queryset = queryset.annotate(
    #         duration_in_days=ExpressionWrapper(
    #             expression=functions.Coalesce(inactive_from, current_date) - functions.Coalesce(active_from, current_date),
    #             output_field=DurationField(),
    #         )
    #     )
        
    #     return queryset
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        current_date = timezone.now().date()

        active_from = F("active_from")
        inactive_from = F("inactive_from")
        queryset = queryset.annotate(
            duration_in_days=ExpressionWrapper(
                expression=Coalesce(inactive_from, current_date) - Coalesce(active_from, current_date),
                output_field=DurationField(),
            ),
            total_income=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("project__income__hours") * F("project__income__hour_rate"),
                        output_field=DecimalField(max_digits=10, decimal_places=2),
                    ),
                    filter=models.Q(project__income__status="approved"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
                0.0,
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
        )
        return queryset
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        
        if request.user.is_superuser:
            return tuple(list_display)
        if request.user.has_perm("project_management.exclude_income"):
            if "get_project_income" in list_display:
                list_display.remove("get_project_income")
        if request.user.has_perm("project_management.exclude_hourly_rate"):
            if "get_hourly_rate" in list_display:
                list_display.remove("get_hourly_rate")
        return tuple(list_display)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.active and obj.inactive_from is None:
            obj.inactive_from = timezone.now().date()
            obj.save()
            obj.project_set.update(active=False)
        elif obj.active:
            if obj.active_from is None:
                obj.active_from = timezone.now().date()
            obj.inactive_from = None
            obj.save()
    
    class Media:
        css = {"all": ("css/list.css", "css/daily-update.css")}


@admin.register(ClientFeedbackEmail)
class ClientFeedbackEmailAdmin(admin.ModelAdmin):
    list_display = ("subject", "feedback_type")

    def has_module_permission(self, request):
        return False


class ClientExperienceForm(forms.ModelForm):
    class Meta:
        model = ClientExperience
        fields = "__all__"

    def clean(self):
        status = self.cleaned_data.get("status")
        follow_up_date = self.cleaned_data.get("follow_up_date")
        meeting_date = self.cleaned_data.get("meeting_date")
        if status == 1 and not follow_up_date:
            raise forms.ValidationError(
                "Follow up date is required. When status is follow up."
            )
        elif status == 2 and not meeting_date:
            raise forms.ValidationError(
                "Meeting date is required. When status is meeting."
            )
        super().clean()


@admin.register(ClientExperience)
class ClientExperienceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        # "web_name",
        "get_project_name",
        "email",
        # "linkedin_url",
        # "get_client_review",
        "country",
        "get_hourly_rate",
        "payment_method",
        "invoice_type",
        "get_client_age",
        "status",
    )
    fields = (
        # "name",
        # "active",
        # "email",
        # "invoice_cc_email",
        # "designation",
        # "company_name",
        # "logo",
        # "is_need_feedback",
        # "client_feedback",
        # "image",
        # "linkedin_url",
        # "bill_from",
        # # "cc_email",
        # "address",
        # "country",
        # "notes",
        # "is_hour_breakdown",
        # "hourly_rate",
        # "active_from",
        # "payment_method",
        # "invoice_type",
        # "review",
        "status",
        "follow_up_date",
        "meeting_date",
    )
    readonly_fields = (
        "name",
        "active",
        "email",
        "invoice_cc_email",
        "designation",
        "company_name",
        "logo",
        "is_need_feedback",
        "client_feedback",
        "image",
        "linkedin_url",
        "bill_from",
        # "cc_email",
        "address",
        "country",
        "notes",
        "is_hour_breakdown",
        "hourly_rate",
        "active_from",
        "payment_method",
        "invoice_type",
        "review",
    )
    list_filter = [
        "is_need_feedback",
        "active",
        "status",
        "review",
        # "payment_method",
        # "invoice_type",
    ]
    # inlines = (ClientInvoiceDateInline, ClientAttachmentInline)
    search_fields = ["name", "web_name"]
    # autocomplete_fields = ["country", "payment_method"]
    form = ClientExperienceForm
    # actions = ["mark_as_in_active"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("project_set")
            .annotate(
                sort_date=Case(
                    When(status=ClientStatus.FOLLOW_UP, then="follow_up_date"),
                    When(status=ClientStatus.MEETING, then="meeting_date"),
                    default=None,
                    output_field=DateField(),
                )
            )
            .order_by("sort_date")
        )

    @admin.display(description="Project Name")
    def get_project_name(self, obj):
        project_name = obj.project_set.all().values_list("title", flat=True)

        return format_html("<br>".join(project_name))

    @admin.display(description="Hourly", ordering="hourly_rate")
    def get_hourly_rate(self, obj):
        if obj.is_active_over_six_months:
            return format_html(f"<span style='color: red;'>{obj.hourly_rate}</span>")
        return obj.hourly_rate

    @admin.display(description="Age", ordering="created_at")
    def get_client_age(self, obj):
        return timesince(obj.created_at)

    def get_list_filter(self, request: HttpRequest):
        if request.user.has_perm("project_management.view_client"):
            return super().get_list_filter(request)
        self.list_filter.remove("payment_method")
        return self.list_filter

    @admin.action(description="Mark as In-active")
    def mark_as_in_active(self, request, queryset):
        try:
            queryset.update(active=False)
            self.message_user(
                request, "Selected clients are marked as active.", message.SUCCESS
            )
        except Exception:
            self.message_user(
                request, "Selected clients are not marked as active.", message.ERROR
            )

    # get_project_name.short_description = "Project Name"
    @admin.display(description="Client Review")
    def get_client_review(self, obj):
        client_review = obj.review.all().values_list("name", flat=True)

        return format_html("<br>".join(client_review))

    # def has_module_permission(self, request):
    #     return False

    def save_model(self, request, obj, form, change):

        if obj.status == ClientStatus.MEETING:
            obj.follow_up_date = None
        elif obj.status == ClientStatus.FOLLOW_UP:
            obj.meeting_date = None
        super().save_model(request, obj, form, change)
        super().save_model(request, obj, form, change)
