import datetime

from django.contrib import admin
from django.db.models import Q, Sum

from config.admin import RecentEdit
from config.admin.utils import simple_request_filter
from project_management.models import EmployeeProjectHour


@admin.register(EmployeeProjectHour)
class EmployeeHourAdmin(RecentEdit, admin.ModelAdmin):
    list_display = ('employee', 'hours', 'project_hour', 'manager')
    list_filter = ('employee', 'created_at',)
    search_fields = ('hours', 'employee__full_name',)
    date_hierarchy = 'project_hour__date'

    change_list_template = 'admin/total.html'

    def manager(self, obj):
        return obj.project_hour.manager

    # query for get total hour by query string
    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        if not request.user.is_superuser:
            qs.filter(project_hour__manager=request.user.employee.id)
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
            return query_set.filter(project_hour__manager=request.user.employee.id)
        return query_set

    def get_list_filter(self, request):
        if not request.user.is_superuser:
            return []
        return super(EmployeeHourAdmin, self).get_list_filter(request)
