from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from account.models import ProjectCommission
from employee.models import Employee


@admin.register(ProjectCommission)
class ProjectCommissionAdmin(admin.ModelAdmin):
    list_display = ('date', 'employee', 'project', 'payment')
    list_filter = ('employee', 'project')
    date_hierarchy = 'date'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('commissions/', self.admin_site.admin_view(self.commission), name='commission'),
        ]
        return my_urls + urls

    def commission(self, request, *args, **kwargs):
        if request.user.is_superuser:
            employee_ids = ProjectCommission.objects.values_list('employee')
            context = dict(
                self.admin_site.each_context(request),
                employees=Employee.objects.filter(active=True, pk__in=employee_ids).all()
            )
            return TemplateResponse(request, "admin/commission/summery.html", context)
        raise PermissionError
