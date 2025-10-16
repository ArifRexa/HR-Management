from datetime import datetime

import nested_admin
from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline
from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib import admin
from django.template.loader import get_template
from django.urls import reverse
from django.utils.html import format_html

from project_management.models import (
    ClientInvoiceDate,
    EnableDailyUpdateNow,
    OurTechnology,
    PlatformImage,
    Project,
    ProjectContent,
    ProjectDocument,
    ProjectEstimation,
    ProjectIndustry,
    ProjectKeyFeature,
    ProjectKeyPoint,
    ProjectNeed,
    ProjectPlatform,
    ProjectReport,
    ProjectResults,
    ProjectResultStatistic,
    ProjectScreenshot,
    ProjectService,
    ProjectServiceSolution,
    ProjectTechnology,
    ProjectToken,
    Tag,
    Teams,
    Technology,
)
from website.models import ProjectKeyword, ProjectMetadata
from website.models import Technology as WebTechnology
from website.models_v2.industries_we_serve import ServeCategory
from website.models_v2.services import ServicePage

from .forms import ProjectTechnologyInlineForm


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


class ProjectContentAdmin(
    SortableStackedInline, nested_admin.NestedStackedInline
):
    model = ProjectContent
    extra = 1
    # fields = ("title", "content", "image", "iframe")
    fields = ("image", "content", "video_url")


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
    exclude = ["canonical"]
    # inlines = [ProjectKeywordInline]


from django.contrib.admin import SimpleListFilter
from django.db.models import Count


class ProjectCountMixin:
    title_field = "title"

    def lookups(self, request, model_admin):
        queryset = self.model.objects.annotate(
            project_count=Count("projects")
        )  # .filter(project_count__gt=0)
        if self.model == ServicePage:
            queryset = queryset.filter(is_parent=True)
        return [
            (obj.id, f"{getattr(obj, self.title_field)} ({obj.project_count})")
            for obj in queryset
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.field_name: self.value()})
        return queryset


class ServiceFilter(ProjectCountMixin, SimpleListFilter):
    title = "Services"
    parameter_name = "services"
    model = ServicePage
    field_name = "services"


class IndustryFilter(ProjectCountMixin, SimpleListFilter):
    title = "Industries"
    parameter_name = "industries"
    model = ServeCategory
    field_name = "industries"


class TechnologyFilter(ProjectCountMixin, SimpleListFilter):
    title = "Technologies"
    parameter_name = "technology"
    model = WebTechnology
    field_name = "technology"
    title_field = "name"

# class ProjectAdminForm(forms.ModelForm):
#     class Meta:
#         model = Project
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Dynamically filter child_services based on selected services
#         if self.instance and self.instance.pk:
#             # Get the selected parent services
#             selected_services = self.instance.services.all()
#             # Get all child services of the selected parent services
#             child_services = ServicePage.objects.filter(
#                 parent__in=selected_services, is_parent=False
#             )
#             # Update the queryset for the child_services field
#             self.fields['child_services'].queryset = child_services
#         else:
#             # If no instance exists (e.g., creating a new project), show no child services
#             self.fields['child_services'].queryset = ServicePage.objects.none()

# class ProjectAdminForm(forms.ModelForm):
#     class Meta:
#         model = Project
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Set child_services to all non-parent services; filtering will happen via JS
#         self.fields['child_services'].queryset = ServicePage.objects.filter(is_parent=False)

# class ProjectAdminForm(forms.ModelForm):
#     class Meta:
#         model = Project
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Set services to parent services only
#         self.fields['services'].queryset = ServicePage.objects.filter(is_parent=True)
#         # Default: all non-parent services
#         self.fields['child_services'].queryset = ServicePage.objects.filter(is_parent=False)


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            "child_services": forms.SelectMultiple()
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Set services to parent services only
    #     self.fields['services'].queryset = ServicePage.objects.filter(is_parent=True)

    #     # Filter child_services based on selected parent services
    #     if self.instance.pk:  # If editing existing project
    #         selected_parent_services = self.instance.services.all()
    #         if selected_parent_services.exists():
    #             # Show only child services whose parent is in the selected services
    #             self.fields['child_services'].queryset = ServicePage.objects.filter(
    #                 is_parent=False,
    #                 parent__in=selected_parent_services
    #             )
    #         else:
    #             # No parent services selected, show none
    #             self.fields['child_services'].queryset = ServicePage.objects.none()
    #     else:  # If creating new project
    #         # No parent services selected yet, show none
    #         self.fields['child_services'].queryset = ServicePage.objects.none()

@admin.register(Project)
class ProjectAdmin(nested_admin.NestedModelAdmin, NonSortableParentAdmin):
    form = ProjectAdminForm
    list_display = (
        "project_title_with_client",
        # "web_title",
        # "client_invoice_date",
        "hourly_rate",
        # "last_increased",
        "active",
        "get_show_in_website",
        "get_report_url",
        "get_cs_link",
        # "get_live_link",
        # "client_feedback_link",
    )
    search_fields = (
        "title",
        "web_title",
        "client__name",
        "client__email",
    )
    date_hierarchy = "created_at"
    inlines = (
        # ProjectResultInline,
        # ProjectKeyPointInline,
        # ProjectTechnologyInline,
        ProjectContentAdmin,
        # ProjectServiceInline,
        # ProjectKeyFeatureInline,
        # ProjectScreenshotInline,
        # ProjectDocumentAdmin,
        # ProjectPlatformImageInline,
        ProjectMetadataInline,
    )

    list_filter = (
        "active",
        "show_in_website",
        ServiceFilter,
        IndustryFilter,
        TechnologyFilter,
    )
    list_per_page = 20
    ordering = ("pk",)
    # autocomplete_fields = ["client"]
    autocomplete_fields = [
        "client",
        "categories_tags",
        "industries",
        "services",
        "technology",
        "child_services"
    ]
    # form = ProjectAdminForm
    fields = (
        "active",
        "show_in_website",
        "is_special",
        "title",
        # "slug",
        # "web_title",
        "description",
        "client",
        "client_designation",
        # "client_web_name",
        "client_image",
        "client_review",
        # "platforms",
        # "categories_tags",
        "services",
        "child_services",
        "technology",
        "industries",
        "live_link",
        "behance_link",
        # "location",
        "country",
        # "is_team",
        # "special_image",
        # "in_active_at",
        "hourly_rate",
        "activate_from",
        # "featured_image",
        # "display_image",
        "project_logo",
        "thumbnail",
        "case_study_pdf",
        "featured_video",
        # "tags",
        # "identifier",
        # "is_highlighted",
        # "project_results",
        # "location_image",
        # "service_we_provide_image",
        # "industry_image",
    )


    change_form_template = "admin/project_management/project/change_form.html"

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['child_services_queryset'] = ServicePage.objects.filter(is_parent=False).select_related('parent')
        return super().changeform_view(request, object_id, form_url, extra_context)


    class Media:
        js = ("admin/js/project_admin.js",)

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

    @admin.display(description="Website", ordering="show_in_website")
    def get_show_in_website(self, obj):
        from django.templatetags.static import static

        if obj.show_in_website:
            icon = static("admin/img/icon-yes.svg")
        else:
            icon = static("admin/img/icon-no.svg")
        return format_html('<img src="{}" alt="{}">', icon, obj.show_in_website)

    @admin.display(description="CS", ordering="identifier")
    def get_cs_link(self, obj):
        html_template = get_template(
            "admin/project_management/list/cs_link.html"
        )
        url = f"https://mediusware.com/case-study/{obj.slug}"
        html_content = html_template.render({"url": url, "obj": obj})
        return format_html(html_content)

    def get_report_url(self, obj):
        html_template = get_template(
            "admin/project_management/list/col_reporturl.html"
        )
        html_content = html_template.render({"identifier": obj.identifier})
        return format_html(html_content)

    get_report_url.short_description = "WU"

    def get_live_link(self, obj):
        html_template = get_template(
            "admin/project_management/list/live_link.html"
        )
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
        return format_html(
            '<span style="color:red;">{}</span>', obj.activate_from
        )

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
        client_date = ClientInvoiceDate.objects.filter(
            clients=obj.client
        ).values_list("invoice_date", flat=True)

        formatted_dates = "<br/>".join(str(date) for date in client_date)
        return format_html(formatted_dates)


@admin.register(ProjectNeed)
class ProjectNeedAdmin(admin.ModelAdmin):
    list_display = ("technology", "quantity", "note")

    def has_module_permission(self, request):
        return False


# @admin.register(ProjectReport)
# class ProjectReportAdmin(admin.ModelAdmin):
#     list_display = ["id", "project", "name", "type", "send_to", "api_token"]
#     list_display_links = ["project"]
#     list_filter = ("project", "type")
#     search_fields = ("project__title", "name", "type")

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'project':
    #         kwargs['queryset'] = Project.objects.filter(active=True)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


# @admin.register(EnableDailyUpdateNow)
# class EnableDailyUpdateNowAdmin(admin.ModelAdmin):
#     list_display = ["name", "enableproject", "last_time"]
#     list_editable = ("enableproject",)

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


# Register Teams models here.
# @admin.register(Teams)
# class TeamsAdmin(admin.ModelAdmin):
#     pass


@admin.register(ProjectEstimation)
class ProjectEstimationAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "date",
        "get_estivate_hours",
        "get_used_hours",
        "get_extra_used_hours",
        "is_active",
    )
    list_filter = ("is_active", "project")
    search_fields = ("project__title",)
    date_hierarchy = "date"
    exclude = ("estimation", "is_active")
    autocomplete_fields = ["project"]

    @admin.display(description="Used Hours", ordering="total_hours_used")
    def get_used_hours(self, obj):
        return obj.total_hours_used

    @admin.display(description="Estimate Hours")
    def get_estivate_hours(self, obj):
        if obj.hours < obj.total_hours_used:
            return format_html(f"<span style='color:red;'>{obj.hours}</span>")
        return obj.hours

    @admin.display(description="Extra Used Hours")
    def get_extra_used_hours(self, obj):
        if obj.hours < obj.total_hours_used:
            return obj.total_hours_used - obj.hours
        return 0

    def save_model(self, request, obj, form, change):
        exist_estimate = ProjectEstimation.objects.filter(
            project=obj.project, is_active=True
        ).exclude(pk=obj.pk)
        if exist_estimate.exists():
            exist_estimate.update(is_active=False)
        return super().save_model(request, obj, form, change)
