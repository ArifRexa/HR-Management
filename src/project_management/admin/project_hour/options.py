import datetime

from django.contrib import admin
from django.template.loader import get_template
from django.utils.html import format_html

from project_management.models import ProjectHour


class ProjectTypeFilter(admin.SimpleListFilter):
    title = 'hour type'
    parameter_name = 'hour_type'

    def lookups(self, request, model_admin):
        return (
            ('bonus', 'Bonus Project Hour'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'bonus':
            return queryset.filter(
                hour_type='bonus',
            )
        return queryset.filter(
                hour_type='project',
            )


class ProjectHourOptions(admin.ModelAdmin):
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
        filters = ['forcast', ProjectTypeFilter, 'project', 'manager', 'date']
        if not request.user.is_superuser:
            filters.remove('manager')
        return filters

    def get_list_display(self, request):
        """

        @type request: object
        """
        list_display = ['date', 'project', 'hours', 'manager', 'get_resources', 'description', 'get_forcast', 'payable']
        if not request.user.is_superuser:
            list_display.remove('payable')
        return list_display

    @admin.display(description='Forcast', ordering='forcast')
    def get_forcast(self, obj: ProjectHour):
        html_template = get_template('admin/project_hour/col_forcast.html')
        html_content = html_template.render({
            'project_hour': obj
        })
        return format_html(html_content)

    @admin.display(description='Resources')
    def get_resources(self, obj: ProjectHour):
        html = ""
        i = 1
        for elem in obj.employeeprojecthour_set.all():
            html += f"<p>{i}.{elem.employee.full_name} ({elem.hours})</p>"
            i += 1
        return format_html(html)

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
