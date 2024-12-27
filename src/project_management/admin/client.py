from django import forms
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.timesince import timesince
from django.contrib import messages as message

# from networkx import project
from project_management.models import (
    Client,
    ClientAttachment,
    ClientExperience,
    ClientFeedbackEmail,
    ClientInvoiceDate,
    ClientReview,
    ClientStatus,
    Country,
    PaymentMethod,
    Project,
    Technology,
    InvoiceType,
)
from django.utils.translation import gettext_lazy as _
from django.db.models import Case, When, DateField


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


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
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
    )
    fields = (
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
        "review",
        "payment_method",
        "invoice_type",
    ]
    inlines = (ClientInvoiceDateInline, ClientAttachmentInline)
    search_fields = ["name", "web_name"]
    autocomplete_fields = ["country", "payment_method"]
    form = ClientForm
    actions = ["mark_as_in_active"]

    @admin.display(description="Project Name")
    def get_project_name(self, obj):
        project_name = obj.project_set.all().values_list("title", flat=True)

        return format_html("<br>".join(project_name))

    @admin.display(description="Hourly Rate", ordering="hourly_rate")
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
        except Exception as e:
            self.message_user(
                request, "Selected clients are not marked as active.", message.ERROR
            )

    # get_project_name.short_description = "Project Name"
    @admin.display(description="Client Review")
    def get_client_review(self, obj):
        client_review = obj.review.all().values_list("name", flat=True)

        return format_html("<br>".join(client_review))

    def has_module_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.active:
            obj.project_set.update(active=False)


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

    @admin.display(description="Hourly Rate", ordering="hourly_rate")
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
        except Exception as e:
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
