import csv

from django.contrib import admin
from django.http import HttpResponse

from project_management.admin.graph.admin import ExtraUrl


class ProjectHourAction(ExtraUrl, admin.ModelAdmin):
    actions = ['export_as_csv', 'enable_payable_status', 'disable_payable_status']

    def get_actions(self, request):
        actions = super().get_actions(request)
        print(actions['export_as_csv'])
        if not request.user.is_superuser:
            del actions['enable_payable_status']
            del actions['disable_payable_status']
        return actions

    @admin.action()
    def enable_payable_status(self, request, queryset):
        queryset.update(payable=True)

    @admin.action()
    def disable_payable_status(self, request, queryset):
        queryset.update(payable=False)

    @admin.action()
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="project_hour.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Date', 'Project', 'Hours', 'Payment', 'Manager'])
        total = 0
        for project_hour in queryset:
            total += project_hour.hours * 10
            writer.writerow([
                project_hour.date,
                project_hour.project,
                project_hour.hours,
                project_hour.hours * 10,
                project_hour.manager
            ])
        writer.writerow(['', 'Total', '', total, ''])
        return response
