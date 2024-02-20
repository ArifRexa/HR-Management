from typing import Any
from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from django_q.tasks import async_task
from django.template import loader
from django.core.mail import EmailMessage

# Register your models here.
from django.template.defaultfilters import (
    truncatechars_html,
)
from django.utils.html import strip_tags, format_html
from django.utils.safestring import mark_safe

from config.utils.pdf import PDF
from employee.models import Employee
from .models import (
    Designation,
    PayScale,
    LeaveManagement,
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


class EmailAnnouncementAttatchmentInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = EmailAnnouncementAttatchment
    extra = 0  


@admin.register(EmailAnnouncement)
class EmailAnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'subject',
    )
    
    actions = (
        'send_mail',
    )

    inlines = (EmailAnnouncementAttatchmentInline,)

    @admin.action(description="Send Email")
    def send_mail(modeladmin, request, queryset):
        for announcement in queryset:
           
                employee_email_list = list(
                    Employee.objects.filter(active=True).values_list("email", flat=True)
                )
                for employee_email in employee_email_list:
                    subject = announcement.subject
                    attachmentqueryset = EmailAnnouncementAttatchment.objects.filter(email_announcement=announcement)
                    attachment_paths = [attachment.attachments.path for attachment in attachmentqueryset]
                    html_body = announcement.body
                    async_task(
                        "settings.tasks.announcement_all_employee_mail", employee_email, subject, html_body, attachment_paths
                    )
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
    amount = forms.IntegerField()


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
                employees = Employee.objects.filter(
                    active=True,
                    lunch_allowance=True,
                ).values_list("id", flat=True)
                for employee in employees:
                    EmployeeFoodAllowance.objects.update_or_create(
                        employee_id=employee,
                        date=form.cleaned_data.get("date"),
                        defaults={
                            "amount": form.cleaned_data.get("amount"),
                        },
                    )
        return redirect("admin:settings_employeefoodallowance_changelist")
