from django.contrib import admin

from project_management.models import Project, ProjectTechnology, ProjectScreenshot, ProjectContent, Technology, \
    ProjectNeed


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    pass


class ProjectTechnologyInline(admin.StackedInline):
    model = ProjectTechnology
    extra = 1


class ProjectScreenshotInline(admin.StackedInline):
    model = ProjectScreenshot
    extra = 1


class ProjectContentInline(admin.StackedInline):
    model = ProjectContent
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'active', 'show_in_website')
    search_fields = ('title', 'client__name', 'client__email')
    date_hierarchy = 'created_at'
    inlines = (ProjectTechnologyInline, ProjectScreenshotInline, ProjectContentInline)


@admin.register(ProjectNeed)
class ProjectNeedAdmin(admin.ModelAdmin):
    list_display = ('technology', 'quantity', 'note')
