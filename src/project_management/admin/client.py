from django import forms
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.timesince import timesince

# from networkx import project
from project_management.models import (
    Client,
    ClientAttachment,
    ClientFeedbackEmail,
    ClientInvoiceDate,
    ClientReview,
    Country,
    PaymentMethod,
    Project,
    Technology,
    InvoiceType,
)
from django.utils.translation import gettext_lazy as _


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
        "project__active",
        "review",
        "payment_method",
        "invoice_type",
    ]
    inlines = (ClientInvoiceDateInline, ClientAttachmentInline)
    search_fields = ["name", "web_name"]
    autocomplete_fields = ["country", "payment_method"]
    form = ClientForm

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
