import datetime

from django.contrib import admin
from django.template.loader import get_template
from django.test import Client
from django.utils.html import format_html
from django.utils.safestring import mark_safe
# from networkx import project

from project_management.models import ProjectHour
from employee.models import Employee
from project_management.models import Project,Client

class ProjectFilter(admin.SimpleListFilter):
    title = 'Project Type'
    parameter_name = 'project__id__exact'

    def lookups(self, request, model_admin):
        project_types = Project.objects.filter(active=True).values_list('id', 'title', 'client__name').distinct()
        choices = []
        for project_id, project_title, client_name in project_types:
            display_name = f"{project_title} ({client_name})" if client_name else project_title
            choices.append((str(project_id), display_name))
        return choices

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': ('All'),
        }

        for lookup, title in self.lookup_choices:
            project = Project.objects.get(pk=lookup)
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': format_html(f'<span style="color: red;">{title}</span>') if not project.check_is_weekly_project_hour_generated else format_html(f'<span style="color: inherit;">{title}</span>')                                         
            }

    def queryset(self, request, queryset):
        project_id = self.value()
        if project_id:
            return queryset.filter(
                project__id=project_id,
            )
        else:
            return queryset
        


class ProjectTypeFilter(admin.SimpleListFilter):
    title = 'hour type'
    parameter_name = 'hour_type'

    def lookups(self, request, model_admin):
        return (
            ('bonus', 'Bonus'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'bonus':
            return queryset.filter(
                hour_type='bonus',
            )
        return queryset.filter(
                hour_type='project',
            )


class ProjectManagerFilter(admin.SimpleListFilter):
    title = 'manager'
    parameter_name = 'manager__id__exact'

    def lookups(self, request, model_admin):
        employees = Employee.objects.filter(active=True, manager=True).values('id', 'full_name')
        return tuple(
            [(emp.get('id'), emp.get('full_name'),) for emp in employees]
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(manager__id__exact=self.value())


class ProjectLeadFilter(admin.SimpleListFilter):
    title = 'lead'
    parameter_name = 'manager__id__exact'

    def lookups(self, request, model_admin):
        employees = Employee.objects.filter(active=True, lead=True).values('id', 'full_name')
        return tuple(
            [(emp.get('id'), emp.get('full_name'),) for emp in employees]
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(manager__id__exact=self.value())

class ProjectClientFilter(admin.SimpleListFilter):
    title = 'client'
    parameter_name = 'client__id__exact'

    def lookups(self, request, model_admin):
        employees = Client.objects.values('id','name')
        return tuple(
            [(emp.get('id'), emp.get('name'),) for emp in employees]
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(project__client__id__exact=self.value())

class ProjectHourOptions(admin.ModelAdmin):
    class Media:
        css = {"all": ("css/list.css",)}
        js = ("js/list.js",)
    # override create / edit fields
    # manager filed will not appear if the authenticate user is not super user
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request)
        if not request.user.is_superuser:
            fields.remove('manager')
            fields.remove('payable')
            if not request.user.has_perm('project_management.select_hour_type'):
                fields.remove('hour_type')
        return fields

    def get_list_filter(self, request):
        filters = [ProjectTypeFilter, ProjectFilter,'date',]
        # if not request.user.is_superuser:
        #     filters.remove('manager')
        return filters

    def get_list_display(self, request):
        """

        @type request: object
        """
        list_display = ['date', 'project', 'hours', 'manager', 'get_resources']
        # if not request.user.is_superuser:
        #     list_display.remove('payable')
        return list_display

    # @admin.display(description='Forcast', ordering='forcast')
    # def get_forcast(self, obj: ProjectHour):
    #     html_template = get_template('admin/project_hour/col_forcast.html')
    #     html_content = html_template.render({
    #         'project_hour': obj
    #     })
    #     return format_html(html_content)

    @admin.display(description='Resources')
    def get_resources(self, obj: ProjectHour):
        html = ""
        i = 1
        for elem in obj.employeeprojecthour_set.all():
            if elem.employee.sqa and elem.hours > 10:
                html += f"<p style='color:red;'>{i}.{elem.employee.full_name} ({elem.hours})</p>"
                i+=1
                continue
            html += f"<p>{i}.{elem.employee.full_name} ({elem.hours})</p>"
            i += 1
        return format_html(html)

    @admin.display(description="Operation Feedback")
    def operation_feedback_link(self, obj):
        html_template = get_template(
            "admin/project_management/list/col_operation_feedback.html"
        )
        rendered_html = html_template.render({"obj": obj})
        return rendered_html
    

    @admin.display(description="Client Experience Feedback")
    def client_exp_feedback_link(self, obj):
        html_template = get_template(
            "admin/project_management/list/col_client_exp_feedback.html"
        )
        rendered_html = html_template.render({"obj": obj})
        return rendered_html

    # @admin.display(description='Project')
    # def get_project(self, obj: ProjectHour):
    #     return format_html(f'<div style="color: red;">{obj.project.title}</div>') if obj.project.check_is_weekly_project_hour_generated == False else format_html(f'<div style="color: inherit;">{obj.project.title}</div>')






    # def get_readonly_fields(self, request, obj=None):
    #     three_day_earlier = datetime.datetime.today() - datetime.timedelta(days=2)
    #     if obj is not None:
    #         print(obj.created_at)
    #         project_hour = ProjectHour.objects.filter(
    #             id=request.resolver_match.kwargs['object_id'],
    #             created_at__gte=three_day_earlier,
    #         ).first()
    #         if project_hour is None and not request.user.is_superuser:
    #             return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
    #     return ()

