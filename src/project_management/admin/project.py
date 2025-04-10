from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any
from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.http import HttpRequest
from django.template.loader import get_template
from django.urls import reverse
from django.utils.html import format_html
from icecream import ic
import nested_admin

from website.models import ProjectKeyword, ProjectMetadata
from .forms import ProjectTechnologyInlineForm, ProjectAdminForm
from django import forms
from django.contrib.sites.shortcuts import get_current_site
from project_management.models import (
    PlatformImage,
    Project,
    ProjectResultStatistic,
    ProjectResults,
    ProjectServiceSolution,
    ProjectTechnology,
    ProjectScreenshot,
    ProjectContent,
    Technology,
    ProjectNeed,
    Tag,
    ProjectDocument,
    ProjectReport,
    EnableDailyUpdateNow,
    ObservationProject,
    ProjectOverview,
    ProjectStatement,
    ProjectChallenges,
    ProjectSolution,
    ProjectKeyFeature,
    OurTechnology,
    ProjectPlatform,
    ProjectIndustry,
    ProjectService,
    ClientInvoiceDate,
    ProjectKeyPoint,
    ProjectToken,
)


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    search_fields = ("name",)

    def has_module_permission(self, request):
        return False


@admin.register(OurTechnology)
class OurTechnologyAdmin(admin.ModelAdmin):
    list_display = ("title", "display_technologies")

    def display_technologies(self, obj):
        return ", ".join([tech.name for tech in obj.technologies.all()])

    display_technologies.short_description = "Technologies"

    def has_module_permission(self, request):
        return False


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


class ProjectTechnologyInline(nested_admin.NestedStackedInline):
    model = ProjectTechnology
    form = ProjectTechnologyInlineForm
    extra = 1
    autocomplete_fields = ["technologies"]


class ProjectKeyPointInline(nested_admin.NestedStackedInline):
    model = ProjectKeyPoint
    extra = 1
    verbose_name = "Special Project Key Point"
    verbose_name_plural = "Special Project Key Points"


class ProjectScreenshotInline(nested_admin.NestedStackedInline):
    model = ProjectScreenshot
    extra = 1


class ProjectDocumentAdmin(admin.StackedInline):
    model = ProjectDocument
    extra = 0


class ProjectContentAdmin(nested_admin.NestedStackedInline):
    model = ProjectContent
    extra = 1
    fields = ("title", "content", "image", "video_url")


class ProjectKeyFeatureInline(nested_admin.NestedStackedInline):
    model = ProjectKeyFeature
    extra = 1
    fields = ("description", "img")


@admin.register(ProjectKeyFeature)
class ProjectKeyFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "img")

    def has_module_permission(self, request):
        return False


@admin.register(ProjectResults)
class ProjectResultsAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "increased_sales",
        "return_on_investment",
        "increased_order_rate",
    )
    search_fields = ("title",)

    def has_module_permission(self, request):
        return False


class ProjectPlatformImageInline(admin.TabularInline):
    model = PlatformImage
    extra = 1


class ProjectServiceInline(nested_admin.NestedStackedInline):
    model = ProjectServiceSolution
    extra = 1


class ProjectResultInline(nested_admin.NestedStackedInline):
    model = ProjectResultStatistic
    extra = 1


class ProjectKeywordInline(nested_admin.NestedTabularInline):
    model = ProjectKeyword
    extra = 1


class ProjectMetadataInline(nested_admin.NestedStackedInline):
    model = ProjectMetadata
    extra = 1
    inlines = [ProjectKeywordInline]


@admin.register(Project)
class ProjectAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        "project_title_with_client",
        "web_title",
        "client_invoice_date",
        "hourly_rate",
        "last_increased",
        "active",
        "get_report_url",
        "get_live_link",
        "client_feedback_link",
    )
    search_fields = (
        "title",
        "web_title",
        "client__name",
        "client__email",
    )
    date_hierarchy = "created_at"
    inlines = (
        ProjectResultInline,
        ProjectKeyPointInline,
        ProjectTechnologyInline,
        ProjectContentAdmin,
        ProjectServiceInline,
        ProjectKeyFeatureInline,
        ProjectScreenshotInline,
        # ProjectDocumentAdmin,
        # ProjectPlatformImageInline,
        ProjectMetadataInline,
    )
    list_filter = ("active", "show_in_website")
    list_per_page = 20
    ordering = ("pk",)
    autocomplete_fields = ["client"]
    form = ProjectAdminForm
    fields = (
        "title",
        "web_title",
        "description",
        "client",
        "client_web_name",
        "client_image",
        "client_review",
        "platforms",
        "industries",
        "services",
        "live_link",
        # "location",
        "country",
        "is_team",
        "active",
        "show_in_website",
        "is_special",
        "special_image",
        # "in_active_at",
        "hourly_rate",
        "activate_from",
        "featured_image",
        "display_image",
        "project_logo",
        "thumbnail",
        "featured_video",
        # "tags",
        # "identifier",
        # "is_highlighted",
        # "project_results",
        # "location_image",
        # "service_we_provide_image",
        # "industry_image",
    )
    # def get_readonly_fields(self, request, obj=None):
    #     if not request.user.is_superuser:
    #         return ['on_boarded_by']
    #     return []

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     if request.user.is_superuser:
    #         form.base_fields["hourly_rate"] = forms.DecimalField(
    #             max_digits=10, decimal_places=2, required=False
    #         )
    #     return form

    def get_fields(self, request, obj):
        fields = super().get_fields(request, obj)
        remove_fields = list(fields)
        if not request.user.is_superuser and not request.user.has_perm(
            "project_management.can_see_hourly_rate"
        ):
            remove_fields.remove("hourly_rate")
        return tuple(remove_fields)

    def get_ordering(self, request):
        return ["title"]

    def get_report_url(self, obj):
        html_template = get_template("admin/project_management/list/col_reporturl.html")
        html_content = html_template.render({"identifier": obj.identifier})
        return format_html(html_content)

    get_report_url.short_description = "hours_breakdown"

    def get_live_link(self, obj):
        html_template = get_template("admin/project_management/list/live_link.html")
        html_content = html_template.render({"project": obj})
        return format_html(html_content)

    get_live_link.short_description = "Live Link"

    def client_feedback_link(self, obj):
        try:
            token = obj.projecttoken.token
            url = reverse("admin:client_feedback", args=[token])
            return format_html(f'<a href="{url}">Client Feedback</a>')
        except ProjectToken.DoesNotExist:
            return "No Token Available"

    # def client_feedback_link(self, obj):
    #     request = self.request  # Use request to get the current site domain
    #     try:
    #         token = obj.projecttoken.token
    #         current_site = get_current_site(request)
    #         domain = current_site.domain
    #         url = f'http://{domain}/client-feedback/{token}/'
    #         return format_html(f'<a href="{url}">Client Feedback</a>')
    #     except ProjectToken.DoesNotExist:
    #         return "No Token Available"

    def last_increased(self, obj):
        six_month_ago = datetime.now().date() - relativedelta(months=6)
        if obj.activate_from and obj.activate_from > six_month_ago:
            return obj.activate_from
        return format_html('<span style="color:red;">{}</span>', obj.activate_from)

    def project_title_with_client(self, obj):
        client_name = obj.client.name if obj.client else "No Client"
        return f"{obj.title} ({client_name})"

    project_title_with_client.short_description = "Title"

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if not request.user.is_superuser:
            list_display = [
                field
                for field in list_display
                if field
                not in (
                    "hourly_rate",
                    "increase_rate",
                    "last_increased",
                    "client_invoice_date",
                )
            ]
        return list_display

    def client_invoice_date(self, obj):
        client_date = ClientInvoiceDate.objects.filter(clients=obj.client).values_list(
            "invoice_date", flat=True
        )

        formatted_dates = "<br/>".join(str(date) for date in client_date)
        return format_html(formatted_dates)


@admin.register(ProjectNeed)
class ProjectNeedAdmin(admin.ModelAdmin):
    list_display = ("technology", "quantity", "note")

    def has_module_permission(self, request):
        return False


@admin.register(ProjectReport)
class ProjectReportAdmin(admin.ModelAdmin):
    list_display = ["id", "project", "name", "type", "send_to", "api_token"]
    list_display_links = ["project"]
    list_filter = ("project", "type")
    search_fields = ("project__title", "name", "type")

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'project':
    #         kwargs['queryset'] = Project.objects.filter(active=True)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(EnableDailyUpdateNow)
class EnableDailyUpdateNowAdmin(admin.ModelAdmin):
    list_display = ["name", "enableproject", "last_time"]
    list_editable = ("enableproject",)

    # def has_view_permission(self, request, obj=None):
    #     # Check if the user has the required permission
    #     if request.user.has_perm('project_management.can_change_daily_update_last_time'):
    #         return True
    #     return False


# @admin.register(ObservationProject)
# class ObservationProjectAdmin(admin.ModelAdmin):
#     list_display = ['project_name', 'created_at']  # Customize the display as per your requirements
#     # list_filter = ['project', 'created_at', 'updated_at']  # Add filters if needed
#     # search_fields = ['project__name', 'author__username']  # Add search fields for easier lookup
#     date_hierarchy = 'created_at'  # Add date hierarchy navigation

# def get_queryset(self, request):
#     # Calculate the date two weeks ago
#     two_weeks_ago = datetime.datetime.now() - datetime.timedelta(weeks=2)
#     # Filter objects that were created within the last two weeks
#     queryset = super().get_queryset(request).filter(created_at__gte=two_weeks_ago)
#     return queryset


@admin.register(ProjectPlatform)
class ProjectPlatformAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_module_permission(self, request):
        return False


@admin.register(ProjectIndustry)
class ProjectIndustryAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_module_permission(self, request):
        return False


@admin.register(ProjectService)
class ProjectServiceAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_module_permission(self, request):
        return False


@admin.register(ProjectTechnology)
class ProjectTechnologyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
    )
    search_fields = ("title",)
    filter_horizontal = ("technologies",)

    def has_module_permission(self, request):
        return False
