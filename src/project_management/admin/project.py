from django.contrib import admin

from project_management.models import Project, ProjectTechnology, ProjectScreenshot, ProjectContent, Technology


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
    inlines = (ProjectTechnologyInline, ProjectScreenshotInline, ProjectContentInline)
