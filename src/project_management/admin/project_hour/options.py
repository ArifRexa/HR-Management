import datetime

from django.contrib import admin

from project_management.models import ProjectHour


class ProjectHourOptions(admin.ModelAdmin):
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

    def get_readonly_fields(self, request, obj=None):
        three_day_earlier = datetime.datetime.today() - datetime.timedelta(days=2)
        if obj is not None:
            project_hour = ProjectHour.objects.filter(
                id=request.resolver_match.kwargs['object_id'],
                created_at__gte=three_day_earlier,
            ).first()
            if project_hour is None and not request.user.is_superuser:
                return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
        return ()
