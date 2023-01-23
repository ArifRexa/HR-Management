import datetime

from django.contrib import admin
from django.db.models import Q, Sum

from config.admin import RecentEdit
from config.admin.utils import simple_request_filter
from project_management.models import EmployeeProjectHour


class ProjectTypeFilter(admin.SimpleListFilter):
    title = 'hour type'
    parameter_name = 'project_hour__hour_type'

    def lookups(self, request, model_admin):
        return (
            ('project', 'Project'),
            ('bonus', 'Bonus'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'bonus':
            return queryset.filter(
                project_hour__hour_type='bonus',
            )
        elif self.value() == 'project':
            return queryset.filter(
                project_hour__hour_type='project',
            )

        return queryset


@admin.register(EmployeeProjectHour)
class EmployeeHourAdmin(RecentEdit, admin.ModelAdmin):
    list_display = ('get_date', 'employee', 'hours', 'get_hour_type', 'project_hour', )
    list_filter = (ProjectTypeFilter, 'employee', 'created_at',)
    search_fields = ('hours', 'employee__full_name',)
    date_hierarchy = 'project_hour__date'
    autocomplete_fields = ('employee', 'project_hour')
    change_list_template = 'admin/total.html'

    @admin.display(description="Date", ordering='project_hour__date')
    def get_date(self, obj):
        return obj.project_hour.date
    
    @admin.display(description="Hour Type", ordering='project_hour__')
    def get_hour_type(self, obj):
        return obj.project_hour.hour_type.title()

    def manager(self, obj):
        return obj.project_hour.manager

    # query for get total hour by query string
    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        if not request.user.is_superuser:
            if request.user.employee.manager:
                qs.filter(Q(project_hour__manager=request.user.employee.id) | Q(employee=request.user.employee))
            else:
                qs.filter(employee=request.user.employee)
        return qs.aggregate(tot=Sum('hours'))['tot']

    # override change list view
    # return total hour count
    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super(EmployeeHourAdmin, self).changelist_view(request, extra_context=my_context)

    def get_queryset(self, request):
        """ Return query_set

        overrides django admin query set
        allow super admin only to see all project hour
        manager's will only see theirs
        @type request: object
        """
        query_set = super(EmployeeHourAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            if request.user.employee.manager:
                return query_set.filter(Q(project_hour__manager=request.user.employee.id) | Q(employee=request.user.employee))
            else:
                return query_set.filter(employee=request.user.employee)
        return query_set.select_related("project_hour")

    def get_list_filter(self, request):
        if not request.user.is_superuser:
            return []
        return super(EmployeeHourAdmin, self).get_list_filter(request)
