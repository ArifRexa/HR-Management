from datetime import datetime, timedelta

import openpyxl
from django import forms
from django.contrib import admin, messages
from django.db.models import Prefetch, Sum
from django.db.models.functions import Abs
from django.http import HttpResponse
from django.shortcuts import redirect

# Register your models here.
from django.template.defaultfilters import (
    truncatechars_html,
)
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe
from django_q import admin as q_admin
from django_q import models as q_models
from django_q.models import Schedule
from django_q.tasks import async_task, schedule

from account.models import (
    EmployeeSalary,
    TDSChallan,
)
from config.utils.pdf import PDF
from employee.models import Employee, EmployeeAttendance
from project_management.models import Client
from settings.models import LeaveManagement

from .models import (
    Announcement,
    Bank,
    Designation,
    EmailAnnouncement,
    EmailAnnouncementAttatchment,
    EmployeeFoodAllowance,
    FinancialYear,
    Letter,
    Notice,
    OpenLetter,
    PayScale,
    PublicHoliday,
    PublicHolidayDate,
)


@admin.register(PayScale)
class PayScaleAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(LeaveManagement)
class LeaveManagementAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    search_fields = ["title"]

    def has_module_permission(self, request):
        return False


@admin.register(FinancialYear)
class FinancialYearAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date", "active")

    actions = [
        "export_employee_tds_report",
        "export_employee_tds_report_inactive",
        "export_tds_pdf_for_active_employee",
        "export_tds_pdf_for_inactive_employee",
    ]

    def get_employee_salary_with_challan(self, obj, active_only: bool):
        """
        Returns Employee queryset.
        Each employee has:
            salary          -> list[EmployeeSalary]
            salary.challans -> list[TDSChallan]  (zero-to-many)
        """
        # helper: salaries in the period
        salaries_qs = (
            EmployeeSalary.objects.filter(
                created_at__date__range=(obj.start_date, obj.end_date)
            )
            .annotate(tds_amount=Abs("loan_emi"))
            .order_by("created_at")
        )

        # helper: annotate each salary with the related year/month
        for sal in salaries_qs:
            sal.year = sal.created_at.year
            sal.month = sal.created_at.month

        # employees + salaries
        employees = (
            Employee.objects.filter(active=active_only)
            .order_by("full_name")
            .prefetch_related(
                Prefetch(
                    "employeesalary_set", queryset=salaries_qs, to_attr="salary"
                )
            )
        )

        # attach the challans manually in Python (single DB hit)
        challan_map = {}
        challans = TDSChallan.objects.filter(
            date__year__range=[obj.start_date.year, obj.end_date.year]
        ).prefetch_related("employee")

        # build { (emp_id, year, month): [challan, challan, …] }
        for ch in challans:
            y, m = ch.date.year, ch.date.month
            for emp in ch.employee.all():
                challan_map.setdefault((emp.id, y, m), []).append(ch)

        # glue everything together
        for emp in employees:
            for sal in emp.salary:
                key = (emp.id, sal.created_at.year, sal.created_at.month)
                sal.challans = challan_map.get(key, [])

        return employees

    @admin.action(description="Export TDS PDF (Active)")
    def export_tds_pdf_for_active_employee(self, request, queryset):
        obj = queryset.first()
        if not obj:
            self.message_user(request, "No record selected.")
            return

        pdf = PDF()
        pdf.template_path = "pdf/tds_report.html"
        pdf.file_name = f"{obj.start_date.year}_{obj.end_date.year}_tds_report"
        pdf.context = {
            "employees": Employee.objects.filter(active=True)
            .select_related()
            .prefetch_related(
                "individual_employee_tds_challan",
                Prefetch(
                    "tdschallan_set",
                    queryset=TDSChallan.objects.filter(tds_order__gte=obj.start_date, tds_order__lte=obj.end_date).order_by("tds_order"),
                    to_attr="tds_challans",
                ),
            ),
            "obj": obj,
            # "tds_challan": tds_challan,
        }
        return pdf.render_to_pdf(download=True)

    @admin.action(description="Export TDS PDF (InActive)")
    def export_tds_pdf_for_inactive_employee(self, request, queryset):
        obj = queryset.first()
        if not obj:
            self.message_user(request, "No record selected.")
            return

        pdf = PDF()
        pdf.template_path = "pdf/tds_report.html"
        pdf.file_name = f"{obj.start_date.year}_{obj.end_date.year}_tds_report"
        pdf.context = {
            "employees": Employee.objects.filter(active=False)
            .select_related()
            .prefetch_related(
                "individual_employee_tds_challan",
                Prefetch(
                    "tdschallan_set",
                    queryset=TDSChallan.objects.all().order_by("tds_order"),
                    to_attr="tds_challans",
                ),
            ),
            "obj": obj
        }
        return pdf.render_to_pdf(download=True)

    def _export_employee_tds_report(self, request, queryset, active_status):
        """Helper function to generate TDS report for specified employee status"""
        obj = queryset.first()
        if not obj:
            self.message_user(request, "No record selected")
            return

        # Create workbook and sheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Salary Report"

        # Define headers
        headers = ["Employee Name"] + [
            month[:3]
            for month in [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
        ]
        ws.append(headers)

        # Filter employees based on active status
        employees = Employee.objects.filter(active=active_status)

        for emp in employees:
            row = [emp.full_name]

            # Fetch relevant salary records
            salaries = EmployeeSalary.objects.filter(
                employee=emp,
                salary_sheet__date__range=(obj.start_date, obj.end_date),
            ).order_by("salary_sheet__date")

            # Map months to values (taking last occurrence per month)
            month_values = {}
            for sal in salaries:
                month_num = sal.salary_sheet.date.month
                month_values[month_num] = abs(
                    sal.loan_emi
                )  # Adjust calculation as needed

            # Populate row with monthly values
            for m in range(1, 13):
                row.append(month_values.get(m, ""))

            ws.append(row)

        # Prepare response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"Salary_Report_{obj.start_date.strftime('%Y%m%d')}_to_{obj.end_date.strftime('%Y%m%d')}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # Save workbook
        wb.save(response)
        return response

    @admin.action(description="Export TDS Excel (Active)")
    def export_employee_tds_report(self, request, queryset):
        return self._export_employee_tds_report(request, queryset, True)

    @admin.action(description="Export TDS Excel (Inactive)")
    def export_employee_tds_report_inactive(self, request, queryset):
        return self._export_employee_tds_report(request, queryset, False)

    # def has_module_permission(self, request):
    #     return False


class PublicHolidayDateInline(admin.TabularInline):
    model = PublicHolidayDate
    extra = 1


@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    inlines = (PublicHolidayDateInline,)
    list_display = ("title", "days")

    def days(self, obj):
        total_days = obj.public_holiday.count()
        date_list = [
            dt for dt in obj.public_holiday.values_list("date", flat=True)
        ]
        print(date_list)
        return "({}) \n {}".format(total_days, date_list)

    def has_module_permission(self, request):
        return False


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "default")

    def has_module_permission(self, request):
        return False


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ("title", "get_header", "get_body", "get_footer")
    actions = ("download_pdf",)

    @admin.display(description="Header")
    def get_header(self, obj):
        safe_value = strip_tags(truncatechars_html(obj.header, 50))
        return mark_safe("&nbsp;".join(safe_value.split(" ")))

    @admin.display(description="Body")
    def get_body(self, obj):
        safe_value = strip_tags(truncatechars_html(obj.body, 200))
        return mark_safe("&nbsp;".join(safe_value.split(" ")))

    @admin.display(description="footer")
    def get_footer(self, obj):
        safe_value = strip_tags(truncatechars_html(obj.footer, 20))
        return mark_safe("&nbsp;".join(safe_value.split(" ")))

    @admin.action(description="Print PDF")
    def download_pdf(self, request, queryset):
        pdf = PDF()
        pdf.template_path = "letter.html"
        pdf.context = {"letters": queryset}
        return pdf.render_to_pdf()

    def print_pdf(self, request, queryset):
        pass


@admin.register(OpenLetter)
class OpenLetterAdmin(admin.ModelAdmin):
    list_display = ("title", "message")

    def has_module_permission(self, request):
        return False


admin.site.unregister([q_models.Success])


@admin.register(q_models.Success)
class SuccessfulTask(q_admin.TaskAdmin):
    date_hierarchy = "started"
    list_filter = ("started",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "get_date",
        "rank",
        "description",
        "is_active",
    )
    date_hierarchy = "start_datetime"

    list_filter = ("is_active",)

    # inlines = [EmailAnnouncementInline]

    actions = (
        "mark_active",
        "mark_inactive",
        "send_mail",
    )

    @admin.display(description="Active Date")
    def get_date(self, obj):
        data = f"{obj.start_datetime}<br>{obj.end_datetime}"
        return format_html(data)

    @admin.action(description="Mark Inactive")
    def mark_inactive(modeladmin, request, queryset):
        queryset.update(is_active=False)
        messages.success(request, "Announcements marked as inactive.")

    @admin.action(description="Mark Active")
    def mark_active(modeladmin, request, queryset):
        queryset.update(is_active=True)
        messages.success(request, "Announcements marked as active.")

    # def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
    #     super().save_model(request, obj, form, change)
    #     self.__send_announcement_mail(request, obj, form, change)
    #     return obj

    # def __send_announcement_mail(self, request, obj, form, change):
    #     async_task("settings.tasks.announcement_mail", obj)

    @admin.action(description="Send Email")
    def send_mail(modeladmin, request, queryset):
        employee_email_list = list(
            Employee.objects.filter(active=True).values_list("email", flat=True)
        )
        for announcement in queryset:
            for employee_email in employee_email_list:
                async_task(
                    "settings.tasks.announcement_mail",
                    employee_email,
                    announcement,
                )
        if queryset:
            messages.success(request, "Email sent successfully.")


class EmailAnnouncementAttatchmentInline(
    admin.TabularInline
):  # or admin.StackedInline for a different layout
    model = EmailAnnouncementAttatchment
    extra = 0


@admin.register(EmailAnnouncement)
class EmailAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("subject",)

    actions = ("send_mail_employee", "send_mail_client")

    inlines = (EmailAnnouncementAttatchmentInline,)

    @admin.action(description="Send Email To All Employees")
    def send_mail_employee(modeladmin, request, queryset):
        chunk_size = 50
        hour = 0
        cc_email = request.user.employee.email
        for announcement in queryset:
            employee_email_list = list(
                Employee.objects.filter(active=True).values_list(
                    "email", flat=True
                )
            )
            for i in range(0, len(employee_email_list), chunk_size):
                chunk_emails = employee_email_list[i : i + chunk_size]

                schedule(
                    "settings.tasks.send_chunk_email",
                    chunk_emails,
                    announcement.id,
                    name=f"Email announcement schedule - {timezone.now().microsecond}",
                    schedule_type=Schedule.ONCE,
                    next_run=timezone.now() + timedelta(hours=hour),
                    cc_email=cc_email,
                )

                hour += 1
        if queryset:
            messages.success(request, "Email sent successfully.")

    @admin.action(description="Send Email To All Clients")
    def send_mail_client(modeladmin, request, queryset):
        chunk_size = 50
        hour = 0
        cc_email = request.user.employee.email
        for announcement in queryset:
            client_email_list = list(
                Client.objects.filter(project__active=True)
                .distinct()
                .values_list("email", flat=True)
            )
            for i in range(0, len(client_email_list), chunk_size):
                chunk_emails = client_email_list[i : i + chunk_size]

                schedule(
                    "settings.tasks.send_chunk_email",
                    chunk_emails,
                    announcement.id,
                    name=f"Email announcement schedule - {timezone.now().microsecond}",
                    schedule_type=Schedule.ONCE,
                    next_run=timezone.now() + timedelta(hours=hour),
                    cc_email=cc_email,
                )

                hour += 1
        if queryset:
            messages.success(request, "Email sent successfully.")


class FoodAllowanceForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
            },
        ),
    )


@admin.register(EmployeeFoodAllowance)
class EmployeeFoodAllowanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "amount", "date")
    date_hierarchy = "date"
    change_list_template = "settings/employee_lunch.html"

    def changelist_view(self, request, extra_context={}):
        extra_context["allowance_form"] = FoodAllowanceForm()
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        urls = [
            path(
                route="generate/",
                view=self.xxx_view,
                name="settings_employeefoodallowance_generate",
            )
        ] + urls
        return urls

    def xxx_view(self, request, **kwargs):
        if request.method == "POST":
            form = FoodAllowanceForm(data=request.POST)
            if form.is_valid():
                date = form.cleaned_data.get("date")
                # amount = form.cleaned_data.get("amount")

                # Get all active employees eligible for lunch allowance
                employees = Employee.objects.filter(
                    active=True, lunch_allowance=True
                )

                year = date.year
                month = date.month

                # Calculate the first and last date of the month
                first_day_of_month = datetime(year, month, 1).date()
                last_day_of_month = datetime(
                    year, month + 1, 1
                ).date() - timedelta(days=1)

                print(first_day_of_month)
                print(last_day_of_month)

                for employee in employees:
                    # Calculate the number of attendance records for the employee on the given date
                    attendance_count = EmployeeAttendance.objects.filter(
                        employee=employee,
                        date__range=[first_day_of_month, last_day_of_month],
                    ).count()

                    # Calculate the number of leave days for the employee on the given date
                    # leave_count = LeaveManagement.objects.filter(
                    #     Q(leave__employee=employee),
                    #     Q(leave__start_date__lte=date),
                    #     Q(leave__end_date__gte=date) | Q(leave__end_date=None),
                    #     status="approved"
                    # ).count()

                    # Calculate the actual days attended (considering leave)
                    # print(employee,attendance_count,leave_count)
                    # actual_days_attended = attendance_count - leave_count

                    # Calculate the adjusted allowance for the employee
                    # if actual_days_attended < amount:
                    #     adjusted_amount = actual_days_attended
                    # else:
                    #     adjusted_amount = amount

                    # Update or create Food Allowance entry
                    EmployeeFoodAllowance.objects.update_or_create(
                        employee=employee,
                        date=date,
                        defaults={
                            "amount": attendance_count,
                        },
                    )

        return redirect("admin:settings_employeefoodallowance_changelist")


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date")
    date_hierarchy = "created_at"
