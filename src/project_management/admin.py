from django.contrib import admin

# Register your models here.
from django.db.models import Sum, Q

from project_management.models import Client, Project, ProjectHour


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'active')


@admin.register(ProjectHour)
class ProjectHourAdmin(admin.ModelAdmin):
    list_display = ('manager', 'project', 'hours', 'date', 'created_by', 'created_at')
    list_filter = ('manager', 'project', 'date')
    date_hierarchy = 'date'

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

    # override project hour save
    # manager id will be authenticate user employee id if the user is not super user
    def save_model(self, request, obj, form, change):
        if not obj.manager_id:
            obj.manager_id = request.user.employee.id
        super().save_model(request, obj, form, change)
