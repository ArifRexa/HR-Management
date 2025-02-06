import csv
from decimal import Decimal

from django.contrib import admin
from django.http import HttpResponse

from account.models import Income
from employee.models.employee import EmployeeUnderTPM
from project_management.admin.graph.admin import ExtraUrl


class ProjectHourAction(ExtraUrl, admin.ModelAdmin):
    actions = [
        "export_as_csv",
        "enable_payable_status",
        "disable_payable_status",
        "create_income",
        "approved_project_hour_status",
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            del actions["enable_payable_status"]
            del actions["disable_payable_status"]
        if not request.user.is_superuser and not request.user.employee.is_tpm:
            del actions["approved_project_hour_status"]
        return actions

    @admin.action()
    def enable_payable_status(self, request, queryset):
        queryset.update(payable=True)

    @admin.action()
    def approved_project_hour_status(self, request, queryset):
        if request.user.employee.is_tpm:
            tpm_project = EmployeeUnderTPM.objects.filter(
            tpm__id__exact=request.user.employee.id,
        ).values_list("project_id", flat=True).distinct()
            queryset.filter(project_id__in=tpm_project).update(status="approved")
        elif request.user.is_superuser:
            queryset.update(status="approved")

    @admin.action()
    def disable_payable_status(self, request, queryset):
        queryset.update(payable=False)

    @admin.action()
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="project_hour.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(["Date", "Project", "Hours", "Payment", "Manager"])
        total = 0
        for project_hour in queryset:
            total += project_hour.hours * 10
            writer.writerow(
                [
                    project_hour.date,
                    project_hour.project,
                    project_hour.hours,
                    project_hour.hours * 10,
                    project_hour.manager,
                ]
            )
        writer.writerow(["", "Total", "", total, ""])
        return response

    @admin.action(description="Create Income")
    def create_income(self, request, queryset):
        income_object = []
        for project_hour in queryset:
            project = project_hour.project
            convert_rate = Decimal(90.0)
            if project.hourly_rate and project.hourly_rate > 0:
                hourly_rate = project.hourly_rate
            else:
                
                hourly_rate = project.client.hourly_rate if project.client else 0.00
            hours = project_hour.hours or 0
            payment = Decimal(hours) * Decimal(hourly_rate) * convert_rate
            pdf_url = None
            if project_hour.report_file:

                if project_hour.report_file.url.__contains__("http"):
                    pdf_url = project_hour.report_file.url
                else:
                    pdf_url = request.build_absolute_uri(project_hour.report_file.url)

            income_object.append(
                Income(
                    project=project,
                    hours=hours,
                    hour_rate=hourly_rate,
                    convert_rate=convert_rate,
                    date=project_hour.date,
                    status="pending",
                    payment=payment,
                    pdf_url=pdf_url,
                )
            )
        Income.objects.bulk_create(income_object)
