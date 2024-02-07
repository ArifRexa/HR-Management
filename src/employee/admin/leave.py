from datetime import date, timedelta
import datetime

from django.contrib import admin, messages
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils import timezone
from django_q.tasks import async_task
from icecream import ic

from employee.models.employee_activity import EmployeeProject
from employee.models import LeaveAttachment, Leave
from employee.models.leave import leave

class LeaveAttachmentInline(admin.TabularInline):
    model = LeaveAttachment
    extra = 0

class FeedbackInline(admin.TabularInline):
    model = leave.LeaveFeedback
    extra = 0


class LeaveManagementInline(admin.TabularInline):
    model = leave.LeaveManagement
    extra = 0
    can_delete = False
    readonly_fields = ("manager", "status", "approval_time")




class LeaveForm(forms.ModelForm):
    placeholder = """
    Sample application with full explanation
    =========================================
    
    Hello sir,

    I am doing home office. Tomorrow there might not be electricity in our area from 8 am to 5 pm.
    That's why I am asking for a leave.
    
    I will join office day after tomorrow.
    
    Thank you.
    Full name    
    """
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": placeholder, "cols": 100, "rows": 15}
        )
    )



    class Meta:
        model = Leave
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(LeaveForm, self).__init__(*args, **kwargs)
        if self.fields.get("message"):
            self.fields["message"].initial = self.placeholder

    

    


@admin.register(Leave)
class LeaveManagement(admin.ModelAdmin):
    actions = ("approve_selected",)
    readonly_fields = ("note", "total_leave")
    exclude = ["status_changed_at", "status_changed_by"]
    inlines = (LeaveAttachmentInline, LeaveManagementInline, FeedbackInline)
    search_fields = ("employee__full_name", "leave_type")
    form = LeaveForm
    date_hierarchy = "start_date"

    def get_list_display(self, request):
        # existing_list = super(LeaveManagement, self).get_list_display(request)
        list_display = [
        "employee",
        "leave_info",
        "leave_type_",
        "total_leave_",
        "manager_approval",
        "status_",
        "date_range",
        'management__feedback',
        
    ]
        if not request.user.has_perm("employee.can_view_display_feedback"):
            if 'management__feedback' in list_display: list_display.remove('management__feedback')
        return list_display


    def get_fields(self, request, obj=None):
        fields = super(LeaveManagement, self).get_fields(request)
        if not request.user.has_perm("employee.can_approve_leave_applications"):
            admin_only = ["status", "employee"]
            for filed in admin_only:
                fields.remove(filed)
        # if not request.user.has_perm("employee.can_view_feedback"):
        #     fields.remove("display_feedback")
        #     print(fields)
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            leave = Leave.objects.filter(
                id=request.resolver_match.kwargs["object_id"]
            ).first()
            if not leave.status == "pending" and not request.user.has_perm(
                "employee.can_approve_leave_applications"
            ):
                return self.readonly_fields + tuple(
                    [item.name for item in obj._meta.fields]
                )
        return ["total_leave", "note"]
  

    def save_form(self, request, form, change):
        if request._files.get('leaveattachment_set-0-attachment') is None and request._post.get('leave_type') == 'medical':
            raise ValidationError({"leaveattachment_set-TOTAL_FORMS":"Attachment is mandatory."})

        return super().save_form(request, form, change)

    def save_model(self, request, obj, form, change):
        if not obj.employee_id:
            obj.employee_id = request.user.employee.id

        if request.user.has_perm("employee.can_approve_leave_applications"):
            obj.status_changed_by = request.user
            obj.status_changed_at = date.today()
        
        super().save_model(request, obj, form, change)



        employee = form.cleaned_data.get("employee") or request.user.employee
        if not change:
            projects = EmployeeProject.objects.get(employee=employee)
            project_obj = EmployeeProject.objects.filter(
                project__in=projects.project.all(), employee__active=True
            )
            from django.db.models import Q

            managers = (
                project_obj.filter(Q(employee__manager=True) | Q(employee__lead=True))
                .exclude(employee__id=employee.id)
                .distinct()
            )

            for manager in managers:
                leave_manage = leave.LeaveManagement(
                    manager=manager.employee, leave=obj
                )
                leave_manage.save()
        self.__send_leave_mail(request, obj, form, change)
        

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("employee.can_approve_leave_applications"):
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ["status", "leave_type", "employee", "start_date"]
        if not request.user.has_perm("employee.can_approve_leave_applications"):
            list_filter.remove("employee")
        return list_filter

    def __send_leave_mail(self, request, obj, form, change):
        if len(form.changed_data) > 0 and "status" in form.changed_data:
            async_task("employee.tasks.leave_mail", obj)
        elif not change:
            async_task("employee.tasks.leave_mail", obj)

    @admin.action()
    def approve_selected(self, request, queryset):
        if request.user.is_superuser or request.user.has_perm(
            "employee.can_approve_leave_applications"
        ):
            messages.success(request, "Leaves approved.")
            queryset.update(status="approved")
        else:
            messages.error(request, "You don't have permission.")

    @admin.display()
    def leave_info(self, leave: Leave):
        year_end_date = leave.end_date.replace(month=12, day=31)
        html_template = get_template("admin/leave/list/col_leave_info.html")
        html_content = html_template.render(
            {
                "casual_passed": leave.employee.leave_passed(
                    "casual", year_end_date.year
                ),
                "casual_remain": leave.employee.leave_available(
                    "casual_leave", year_end_date
                ),
                "medical_passed": leave.employee.leave_passed(
                    "medical", year_end_date.year
                ),
                "medical_remain": leave.employee.leave_available(
                    "medical_leave", year_end_date
                ),
                # 'leave_day':leave.start_date.strftime("%A")
            }
        )
        return format_html(html_content)

    @admin.display()
    def manager_approval(self, obj):
        leave_management = leave.LeaveManagement.objects.filter(leave=obj)
        html_template = get_template("admin/leave/list/col_manager_approval.html")
        html_content = html_template.render({"leave_management": leave_management})

        return format_html(html_content)

    @admin.display()
    def leave_type_(self, leave: Leave):
        html_template = get_template("admin/leave/list/col_leave_day.html")
        html_content = html_template.render(
            {
                # 'use_get_display':True,
                "data": leave.get_leave_type_display(),
                "leave_day": leave.end_date.strftime("%A"),
                "has_friday": has_friday_between_dates(
                    leave.start_date, leave.end_date
                ),
                "has_monday": has_monday_between_dates(
                    leave.start_date, leave.end_date
                ),
            }
        )
        return format_html(html_content)

    @admin.display()
    def total_leave_(self, leave: Leave):
        html_template = get_template("admin/leave/list/col_leave_day.html")
        html_content = html_template.render(
            {
                "data": leave.total_leave,
                "leave_day": leave.end_date.strftime("%A"),
                "has_friday": has_friday_between_dates(
                    leave.start_date, leave.end_date
                ),
                "has_monday": has_monday_between_dates(
                    leave.start_date, leave.end_date
                ),
            }
        )
        return format_html(html_content)

    @admin.display()
    def status_(self, leave: Leave):
        html_template = get_template("admin/leave/list/col_leave_day.html")
        html_content = html_template.render(
            {
                # 'use_get_display':True,
                "data": leave.get_status_display(),
                "leave_day": leave.end_date.strftime("%A"),
                "has_friday": has_friday_between_dates(
                    leave.start_date, leave.end_date
                ),
                "has_monday": has_monday_between_dates(
                    leave.start_date, leave.end_date
                ),
            }
        )
        return format_html(html_content)

    # @admin.display()
    # def start_date_(self, leave: Leave):
    #     html_template = get_template("admin/leave/list/col_leave_day.html")
    #     html_content = html_template.render(
    #         {
    #             "data": leave.start_date,
    #             "leave_day": leave.start_date.strftime("%A"),
    #             "has_friday": has_friday_between_dates(
    #                 leave.start_date, leave.end_date
    #             ),
    #             "has_monday": has_monday_between_dates(
    #                 leave.start_date, leave.end_date
    #             ),
    #         }
    #     )
    #     return format_html(html_content)

    # @admin.display()
    # def end_date_(self, leave: Leave):
    #     html_template = get_template("admin/leave/list/col_leave_day.html")
    #     html_content = html_template.render(
    #         {
    #             "data": leave.end_date,
    #             "leave_day": leave.end_date.strftime("%A"),
    #             "has_friday": has_friday_between_dates(
    #                 leave.start_date, leave.end_date
    #             ),
    #             "has_monday": has_monday_between_dates(
    #                 leave.start_date, leave.end_date
    #             ),
    #         }
    #     )
    #     return format_html(html_content)
    
    # @admin.display(description='Created By')
    # def creator(self, leave: Leave):
    #     return f'{leave.created_by.first_name} {leave.created_by.last_name}'.title()

    @admin.display(description='Date (start date / end date)')
    def date_range(self, leave: Leave):
        return f"{leave.start_date.strftime('%Y-%m-%d')} / {leave.end_date.strftime('%Y-%m-%d')}"


def has_friday_between_dates(start_date, end_date):
    # Create a timedelta of one day
    one_day = timedelta(days=1)

    # Initialize the current date with the start date
    current_date = start_date

    while current_date <= end_date:
        # Check if the current date is a Friday (day number 4, where Monday is 0 and Sunday is 6)
        if current_date.weekday() == 4:
            return True
        current_date += one_day  # Move to the next day

    return False

def has_monday_between_dates(start_date, end_date):
    # Create a timedelta of one day
    one_day = timedelta(days=1)

    # Initialize the current date with the start date
    current_date = start_date

    while current_date <= end_date:
        # Check if the current date is a Friday (day number 4, where Monday is 0 and Sunday is 6)
        if current_date.weekday() == 0:
            return True
        current_date += one_day  # Move to the next day

    return False


@admin.register(leave.LeaveManagement)
class LeaveManagementAdmin(admin.ModelAdmin):
    list_display = [
        "get_employee",
        "get_apply_date",
        "get_leave_type",
        "manager",
        "status",
        "get_leave_date",
        "approval_time",
    ]
    readonly_fields = ("manager", "leave")
    actions = ("approve_selected", "pending_selected", "rejected_selected")
    fields = ("leave", "manager", "status")
    list_filter = ("status", "leave__leave_type", "manager", "leave__employee")
    search_fields = ("manager__full_name", "status")
    date_hierarchy = "created_at"

    @admin.display(description="Employee")
    def get_employee(self, obj):
        return obj.leave.employee.full_name

    @admin.display(description="Application Time")
    def get_apply_date(self, obj):
        return obj.leave.created_at

    @admin.display(description="Leave Type")
    def get_leave_type(self, obj):
        return obj.leave.get_leave_type_display()

    @admin.display(description="Leave On")
    def get_leave_date(self, obj):
        html_template = get_template("admin/leave/list/col_leave_on.html")
        html_content = html_template.render(
            {"start_date": obj.leave.start_date, "end_date": obj.leave.end_date}
        )
        return format_html(html_content)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            obj.approval_time = timezone.now()
            obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(manager=request.user.employee)

    @admin.action()
    def approve_selected(self, request, queryset):
        if request.user.is_superuser or request.user.has_perm(
            "employee.change_leavemanagement"
        ):
            messages.success(request, "Leaves approved.")
            queryset.update(status="approved", approval_time=timezone.now())
        else:
            messages.error(request, "You don't have permission.")

    @admin.action()
    def pending_selected(self, request, queryset):
        if request.user.is_superuser or request.user.has_perm(
            "employee.change_leavemanagement"
        ):
            messages.success(request, "Leaves pending.")
            queryset.update(status="pending")
        else:
            messages.error(request, "You don't have permission.")

    @admin.action()
    def rejected_selected(self, request, queryset):
        if request.user.is_superuser or request.user.has_perm(
            "employee.change_leavemanagement"
        ):
            messages.success(request, "Leaves rejected.")
            queryset.update(status="rejected")
        else:
            messages.error(request, "You don't have permission.")
