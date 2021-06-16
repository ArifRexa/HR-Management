import json

from django.contrib import admin

# Register your models here.
from django.db.models import Sum, Q, F

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

    # query for get total hour by query string
    def get_total_hour(self, request):
        filters = {}
        for key in dict(request.GET):
            filters[key] = request.GET.get(key)
        # only super admin can able to see all
        if not request.user.is_superuser:
            filters['manager__id__exact'] = request.user.employee.id
        dataset = ProjectHour.objects.filter(*[Q(**{key: value}) for key, value in filters.items() if value])
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
        list_display = ['manager', 'project', 'hours', 'date', 'created_by', 'created_at', 'payable']
        if not request.user.is_superuser:
            list_display.remove('payable')
        return list_display

    def get_queryset(self, request):
        query_set = super(ProjectHourAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return query_set.filter(manager_id=request.user.employee.id)
        return query_set

    # override project hour save
    # manager id will be authenticate user employee id if the user is not super user
    def save_model(self, request, obj, form, change):
        if not obj.manager_id:
            obj.manager_id = request.user.employee.id
        super().save_model(request, obj, form, change)

    def enable_payable_status(self, request, queryset):
        queryset.update(payable=True)

    def disable_payable_status(self, request, queryset):
        queryset.update(payable=False)
