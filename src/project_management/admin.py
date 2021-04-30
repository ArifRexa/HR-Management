from django.contrib import admin

# Register your models here.
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum, Q

from project_management.models import Client, Project, ProjectHour


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')


admin.site.register(Client, ClientAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'active')


admin.site.register(Project, ProjectAdmin)


class ProjectHourAdmin(admin.ModelAdmin):
    list_display = ('manager', 'project', 'hours', 'date', 'created_by', 'created_at')
    list_filter = ('manager', 'project', 'date')
    date_hierarchy = 'date'

    change_list_template = 'admin/project_management/extras/total.html'

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

    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super(ProjectHourAdmin, self).changelist_view(request, extra_context=my_context)


admin.site.register(ProjectHour, ProjectHourAdmin)
