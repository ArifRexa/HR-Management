from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any
from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.http import HttpRequest
from django.template.loader import get_template
from django.utils.html import format_html
from icecream import ic
from .forms import ProjectTechnologyInlineForm,ProjectAdminForm
from django import forms
from project_management.models import Project, ProjectTechnology, ProjectScreenshot, ProjectContent, Technology, ProjectNeed, Tag, ProjectDocument, ProjectReport, EnableDailyUpdateNow, ObservationProject,ProjectOverview, ProjectStatement, ProjectChallenges ,ProjectSolution, ProjectKeyFeature,ProjectResults,OurTechnology, ProjectPlatform, ProjectIndustry, ProjectService,ClientInvoiceDate

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

@admin.register(OurTechnology)
class OurTechnologyAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_technologies')

    def display_technologies(self, obj):
        return ", ".join([tech.name for tech in obj.technologies.all()])

    display_technologies.short_description = 'Technologies'
    
    def has_module_permission(self, request):
        return False

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


class ProjectTechnologyInline(admin.StackedInline):
    model = ProjectTechnology
    form = ProjectTechnologyInlineForm
    extra = 1
    


class ProjectScreenshotInline(admin.StackedInline):
    model = ProjectScreenshot
    extra = 1



class ProjectDocumentAdmin(admin.StackedInline):
    model = ProjectDocument
    extra = 0

class ProjectContentAdmin(admin.StackedInline):
    model = ProjectContent
    extra = 1

class ProjectKeyFeatureInline(admin.StackedInline):
    model = ProjectKeyFeature
    extra = 1

@admin.register(ProjectKeyFeature)
class ProjectKeyFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'img')
    
    def has_module_permission(self, request):
        return False


    
@admin.register(ProjectResults)
class ProjectResultsAdmin(admin.ModelAdmin):
    list_display = ('title', 'increased_sales', 'return_on_investment', 'increased_order_rate')
    search_fields = ('title',)

    def has_module_permission(self, request):
        return False



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_title_with_client', 'web_title', 'client_invoice_date','hourly_rate','last_increased', 'active','get_report_url','get_live_link')
    search_fields = ('title', 'web_title', 'client__name', 'client__email',)
    date_hierarchy = 'created_at'
    inlines = (ProjectTechnologyInline,ProjectContentAdmin,ProjectKeyFeatureInline, ProjectScreenshotInline,ProjectDocumentAdmin)
    list_filter = ('active', 'show_in_website')
    list_per_page = 20
    ordering = ('pk',)
    autocomplete_fields = ['client']
    form = ProjectAdminForm
    # def get_readonly_fields(self, request, obj=None):
    #     if not request.user.is_superuser:
    #         return ['on_boarded_by']
    #     return []

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            form.base_fields['hourly_rate'] = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
        return form
    
    def get_fields(self, request, obj):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            fields.remove('hourly_rate')
        return fields
    
    def get_ordering(self, request):
        return ['title']

    def get_report_url(self, obj):
        html_template = get_template("admin/project_management/list/col_reporturl.html")
        html_content = html_template.render({'identifier': obj.identifier})
        return format_html(html_content)
    get_report_url.short_description = 'hours_breakdown'

    def get_live_link(self, obj):
        html_template = get_template("admin/project_management/list/live_link.html")
        html_content = html_template.render({'project': obj})
        return format_html(html_content)
    get_live_link.short_description = 'Live Link'

    def last_increased(self,obj):
        six_month_ago = datetime.now().date() - relativedelta(months=6)
        if obj.activate_from and obj.activate_from > six_month_ago:
            return obj.activate_from
        return format_html('<span style="color:red;">{}</span>', obj.activate_from)

    def project_title_with_client(self, obj):
        client_name = obj.client.name if obj.client else "No Client"
        return f"{obj.title} ({client_name})"
    project_title_with_client.short_description = 'Title'
    
    

    def get_list_display(self, request):
        
        list_display = super().get_list_display(request)
        if not request.user.is_superuser:
            list_display = [field for field in list_display if field not in ('hourly_rate', 'increase_rate', 'last_increased','client_invoice_date')]
        return list_display
    
    def client_invoice_date(self,obj):
        client_date = ClientInvoiceDate.objects.filter(clients=obj.client).values_list('invoice_date',flat=True)

        formatted_dates = "<br/>".join(str(date) for date in client_date)
        return format_html(formatted_dates)

@admin.register(ProjectNeed)
class ProjectNeedAdmin(admin.ModelAdmin):
    list_display = ('technology', 'quantity', 'note')

    def has_module_permission(self, request):
        return False


@admin.register(ProjectReport)
class ProjectReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'name', 'type', 'send_to', 'api_token']
    list_display_links = ['project']
    list_filter = ('project', 'type')
    search_fields = ('project__title', 'name', 'type')

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'project':
    #         kwargs['queryset'] = Project.objects.filter(active=True)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(EnableDailyUpdateNow)
class EnableDailyUpdateNowAdmin(admin.ModelAdmin):
    list_display = ['name','enableproject', 'last_time']
    list_editable = ('enableproject',)

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
    list_display = ('title',)

    def has_module_permission(self, request):
        return False

@admin.register(ProjectIndustry)
class ProjectIndustryAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_module_permission(self, request):
        return False

@admin.register(ProjectService)
class ProjectServiceAdmin(admin.ModelAdmin):
    list_display = ('title',)

    def has_module_permission(self, request):
        return False
    


@admin.register(ProjectTechnology)
class ProjectTechnologyAdmin(admin.ModelAdmin):
    list_display = ('title', 'project',)
    search_fields = ('title',)
    filter_horizontal = ('technologies',)

    def has_module_permission(self, request):
        return False