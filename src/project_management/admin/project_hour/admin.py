import datetime
import json
from datetime import timedelta

from django.contrib import admin

# Register your models here.
from django.db.models import Sum, Q, F
from django.template.context_processors import request
from django.utils import timezone

from config.admin import ExportCsvMixin, RecentEdit
from config.admin.utils import simple_request_filter
from project_management.admin.project_hour.actions import ProjectHourAction
from project_management.admin.project_hour.options import ProjectHourOptions
from project_management.models import Client, Project, ProjectHour, EmployeeProjectHour


class EmployeeHourAdmin(admin.TabularInline):
    model = EmployeeProjectHour
    extra = 1

    # autocomplete_fields = ('employee',)

    def get_readonly_fields(self, request, obj=None):
        three_day_earlier = timezone.now() - timedelta(days=2)
        if obj is not None:
            if obj.created_at <= three_day_earlier and not request.user.is_superuser:
                return ('hours', 'employee')
        return ()


@admin.register(ProjectHour)
class ProjectHourAdmin(ProjectHourAction, ProjectHourOptions, RecentEdit, admin.ModelAdmin):
    date_hierarchy = 'date'
    search_fields = ['hours', 'manager__full_name', 'project__title', 'date']
    inlines = (EmployeeHourAdmin,)
    change_list_template = 'admin/total.html'
    autocomplete_fields = ['project']
    list_per_page = 20
    ordering = ('-pk',)

    # query for get total hour by query string
    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        if not request.user.is_superuser:
            qs.filter(manager__id__exact=request.user.employee.id)
        return qs.aggregate(tot=Sum('hours'))['tot']

    # override change list view
    # return total hour count
    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super(ProjectHourAdmin, self).changelist_view(request, extra_context=my_context)

    def get_queryset(self, request):
        """ Return query_set

        overrides django admin query set
        allow super admin only to see all project hour
        manager's will only see theirs
        @type request: object
        """
        query_set = super(ProjectHourAdmin, self).get_queryset(request)
        if not request.user.is_superuser and not request.user.has_perm('project_management.show_all_hours'):
            print('inside')
            return query_set.filter(manager_id=request.user.employee.id)
        return query_set

    def save_model(self, request, obj, form, change):
        """
        override project hour save
        manager id will be authenticate user employee id if the user is not super user
        """
        if not obj.manager_id:
            obj.manager_id = request.user.employee.id
        super().save_model(request, obj, form, change)
