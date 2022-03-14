from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html

from config.widgets.mw_select_multiple import EmployeeFilteredSelectMultiple
from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery
from employee.models import Employee
from project_management.models import DurationUnit, ProjectResource, ProjectResourceEmployee


@admin.register(DurationUnit)
class DurationUnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_in_hour')


class ProjectResourceEmployeeInline(admin.TabularInline):
    model = ProjectResourceEmployee
    extra = 1
    readonly_fields = ['duration_hour']


@admin.register(ProjectResource)
class ProjectResourceAdmin(admin.ModelAdmin):
    list_display = ('project', 'get_duration', 'manager', 'get_employees', 'active')
    list_filter = ('project', 'manager')
    search_fields = ('project', 'manager')
    inlines = (ProjectResourceEmployeeInline,)

    def save_model(self, request, obj, form, change):
        """
        override project hour save
        manager id will be authenticate user employee id if the user is not super user
        """
        if not obj.manager_id:
            obj.manager_id = request.user.employee.id
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request)
        if not request.user.is_superuser:
            fields.remove('manager')
        return fields

    @admin.display(description='Employees')
    def get_employees(self, obj: ProjectResource):
        return 'asfd'

    @admin.display(description='Project Duration')
    def get_duration(self, obj: ProjectResource):
        return f'Hello'

    def get_queryset(self, request):
        """ Return query_set

        overrides django admin query set
        allow super admin only to see all project hour
        manager's will only see theirs
        @type request: object
        """
        query_set = super(ProjectResourceAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return query_set.filter(manager_id=request.user.employee.id)
        return query_set

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('daily-activity/', self.my_view, name='activity'),
        ]
        return my_urls + urls

    def my_view(self, request, *args, **kwargs):
        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            employees=Employee.objects.filter(active=True, manager=False).all()
        )
        return TemplateResponse(request, "admin/project_resource/daily-activity.html", context)
