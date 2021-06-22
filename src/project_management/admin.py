import datetime
import json
from datetime import timedelta

from django.contrib import admin

# Register your models here.
from django.db.models import Sum, Q, F
from django.template.context_processors import request

from config.admin import ExportCsvMixin
from project_management.models import Client, Project, ProjectHour


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'active')


@admin.register(ProjectHour)
class ProjectHourAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    actions = ['export_as_csv', 'enable_payable_status', 'disable_payable_status']
    search_fields = ['hours', 'manager__full_name', 'project__title', 'date']

    change_list_template = 'admin/total.html'

    list_per_page = 20

    # query for get total hour by query string
    def get_total_hour(self, request):
        filters = dict([(key, request.GET.get(key)) for key in dict(request.GET) if key not in ['p', 'q']])
        dataset = super(ProjectHourAdmin, self).get_queryset(request).filter(
            *[Q(**{key: value}) for key, value in filters.items() if value]
        )
        return dataset.aggregate(tot=Sum('hours'))['tot']

    # override change list view
    # return total hour count
    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super(ProjectHourAdmin, self).changelist_view(request, extra_context=my_context)

    # override create / edit fields
    # manager filed will not appear if the authenticate user is not super user
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request)
        if not request.user.is_superuser:
            fields.remove('manager')
            fields.remove('payable')
        return fields

    def get_list_filter(self, request):
        filters = ['manager', 'project', 'date']
        if not request.user.is_superuser:
            filters.remove('manager')
        return filters

    def get_list_display(self, request):
        """

        @type request: object
        """
        list_display = ['manager', 'project', 'hours', 'date', 'created_by', 'created_at', 'payable']
        if not request.user.is_superuser:
            list_display.remove('payable')
        return list_display

    def get_queryset(self, request):
        """ Return query_set

        overrides django admin query set
        allow super admin only to see all project hour
        manager's will only see theirs
        @type request: object
        """
        query_set = super(ProjectHourAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
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

    def change_view(self, request, *args, **kwargs):
        """
        Change view to readonly filed if the project hour created more then 2 days ago
        """
        self.readonly_fields = ()
        three_day_earlier = datetime.datetime.today() - timedelta(days=2)
        print(three_day_earlier)
        project_hour = ProjectHour.objects.filter(
            id=kwargs['object_id'],
            created_at__gte=three_day_earlier
        ).first()
        if not project_hour and not request.user.is_superuser:
            self.readonly_fields = super(ProjectHourAdmin, self).get_fields(request)
        return super(ProjectHourAdmin, self).change_view(request, *args, **kwargs)

    def enable_payable_status(self, request, queryset):
        queryset.update(payable=True)

    def disable_payable_status(self, request, queryset):
        queryset.update(payable=False)
