from ast import List
import re
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html

# from networkx import project
from project_management.models import (
    Client,
    ClientInvoiceDate,
    ClientReview,
    PaymentMethod,
    Project,
    Technology,
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


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "get_project_name",
        "email",
        "linkedin_url",
        "get_client_review",
        "country",
        "payment_method",
    )
    fields = (
        "name",
        "email",
        "logo",
        "client_feedback",
        "image",
        "linkedin_url",
        "bill_from",
        "cc_email",
        "address",
        "country",
        "notes",
        "is_hour_breakdown",
        "payment_method",
        "review",
    )
    list_filter = ["project__active", "review", "payment_method"]
    inlines = (ClientInvoiceDateInline,)
    search_fields = ["name"]

    @admin.display(description="Project Name")
    def get_project_name(self, obj):
        project_name = obj.project_set.all().values_list("title", flat=True)

        return format_html("<br>".join(project_name))

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
