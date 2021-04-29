from django.contrib import admin

# Register your models here.
from django.db.models import Sum

from project_management.models import Client, Project, ProjectHour


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')


admin.site.register(Client, ClientAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'active')


admin.site.register(Project, ProjectAdmin)


class ProjectHourAdmin(admin.ModelAdmin):
    list_display = ('manager', 'project', 'hours', 'created_by')
    list_filter = ('manager', 'project', 'date')

    change_list_template = 'admin/project_management/extras/total.html'

    def get_total_hour(self, request):
        qs = super().get_queryset(request)
        print(qs)
        print(request)
        total = ProjectHour.objects.all().aggregate(tot=Sum('hours'))['tot']
        return total

    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super(ProjectHourAdmin, self).changelist_view(request, extra_context=my_context)


admin.site.register(ProjectHour, ProjectHourAdmin)
