import csv

from django.contrib import admin

# Register your models here.
from django.db.models import Sum, Q
from django.http import HttpResponse

from config.admin.ExportCsvMixin import ExportCsvMixin
from project_management.models import Client, Project, ProjectHour


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'active')


@admin.register(ProjectHour)
class ProjectHourAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('manager', 'project', 'hours', 'date', 'created_by', 'created_at')
    date_hierarchy = 'date'
    actions = ['export_as_csv']
    search_fields = ['hours', 'manager__full_name', 'project__title', 'date']

    change_list_template = 'admin/total.html'

    # query for get total hour by query string
    def get_total_hour(self, request):
        filters = {
            'date__lt': request.GET.get('date__lt'),
            'date__gte': request.GET.get('date__gte'),
            'manager__id__exact': request.GET.get('manager__id__exact'),
            'project__id__exact': request.GET.get('project__id__exact'),
            'date__month': request.GET.get('date__month'),
            'date__year': request.GET.get('date__year'),
        }
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
        return fields

    def get_list_filter(self, request):
        filters = ['manager', 'project', 'date']
        if not request.user.is_superuser:
            filters.remove('manager')
        return filters

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
