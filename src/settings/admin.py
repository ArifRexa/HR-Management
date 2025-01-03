import re
from typing import Any
from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from django.template import loader
from django.core.mail import EmailMessage
from datetime import timedelta
from django.utils import timezone
from django_q.tasks import async_task, schedule
from django_q.models import Schedule
from datetime import datetime

# Register your models here.
from django.template.defaultfilters import (
    truncatechars_html,
)
from django.utils.html import strip_tags, format_html
from django.utils.safestring import mark_safe

from config.utils.pdf import PDF
from employee.models import Employee
from project_management.models import Client
from .models import (
    Designation,
    Notice,
    PayScale,
    PublicHoliday,
    PublicHolidayDate,
    Bank,
    Letter,
    OpenLetter,
    FinancialYear,
    Announcement,
    EmployeeFoodAllowance,
    EmailAnnouncement,
    EmailAnnouncementAttatchment,
)
from django_q import models as q_models
from django_q import admin as q_admin
from datetime import timedelta
from django.db.models import Q
from employee.models import EmployeeAttendance
from settings.models import LeaveManagement


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

    def has_module_permission(self, request):
        return False


class PublicHolidayDateInline(admin.TabularInline):
    model = PublicHolidayDate
    extra = 1


@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    inlines = (PublicHolidayDateInline,)
    list_display = ("title", "days")

    def days(self, obj):
        total_days = obj.public_holiday.count()
        date_list = [dt for dt in obj.public_holiday.values_list("date", flat=True)]
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
                    "settings.tasks.announcement_mail", employee_email, announcement
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
                Employee.objects.filter(active=True).values_list("email", flat=True)
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
                employees = Employee.objects.filter(active=True, lunch_allowance=True)

                year = date.year
                month = date.month

                # Calculate the first and last date of the month
                first_day_of_month = datetime(year, month, 1).date()
                last_day_of_month = datetime(year, month + 1, 1).date() - timedelta(
                    days=1
                )

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
