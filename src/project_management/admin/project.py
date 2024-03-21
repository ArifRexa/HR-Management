import datetime

from django.contrib import admin
from django.template.loader import get_template
from django.utils.html import format_html
from icecream import ic

from project_management.models import Project, ProjectTechnology, ProjectScreenshot, ProjectContent, Technology, ProjectNeed, Tag, ProjectDocument, ProjectReport, EnableDailyUpdateNow, ObservationProject



@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


class ProjectTechnologyInline(admin.StackedInline):
    model = ProjectTechnology
    extra = 1


class ProjectScreenshotInline(admin.StackedInline):
    model = ProjectScreenshot
    extra = 1


class ProjectContentInline(admin.StackedInline):
    model = ProjectContent
    extra = 1

class ProjectDocumentAdmin(admin.StackedInline):
    model = ProjectDocument
    extra = 0

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'active', 'show_in_website', 'get_report_url')
    search_fields = ('title', 'client__name', 'client__email')
    date_hierarchy = 'created_at'
    inlines = (ProjectTechnologyInline, ProjectScreenshotInline, ProjectContentInline, ProjectDocumentAdmin)
    list_filter = ('active', 'show_in_website')
    list_per_page = 20
    ordering = ('pk',)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ['on_boarded_by']
        return []
    

    def get_ordering(self, request):
        return ['title']

    def get_report_url(self, obj, request):
        html_template = get_template(
            "admin/project_management/list/col_reporturl.html"
        )
        html_content = html_template.render(
            {
                'identifier': obj.identifier,
                'request': request,  # Pass the request to the template context
            }
        )

        return format_html(html_content)

    get_report_url.short_description = 'Report URL'

    def get_list_display(self, request):
        # Override get_list_display to pass the request to the method
        list_display = super().get_list_display(request)
        if 'get_report_url' in list_display:
            list_display = list(list_display)  # Convert to a list if it's a tuple
            idx = list_display.index('get_report_url')
            list_display[idx] = lambda obj: self.get_report_url(obj, request)
        return list_display


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
