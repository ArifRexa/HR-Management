from datetime import date, timedelta, time
import datetime

from django.utils.html import format_html
from django.contrib import admin, messages
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils import timezone
from django_q.tasks import async_task
from icecream import ic
from django.core.mail import EmailMessage
from employee.models.employee_activity import EmployeeProject
from employee.models import LeaveAttachment, Leave
from employee.models.leave import leave


class LeaveAttachmentInline(admin.TabularInline):
    model = LeaveAttachment
    extra = 1


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

    def has_emergency_leave_last_3_months(self, employee):
        # Get the current date and calculate the date 3 months ago
        current_date = timezone.now().date()
        three_months_ago = current_date - timedelta(days=90)

        # Query leaves for the given employee, checking for 'emergency_leave' in the last 3 months
        emergency_leaves = Leave.objects.filter(
            employee=employee,
            applied_leave_type="emergency_leave",
            created_at__date__gte=three_months_ago,
            created_at__date__lte=current_date,
        )

        # Return True if there's at least 1 emergency leave in the last 3 months
        return emergency_leaves.exists()

    def clean(self):
        user = self.request.user
        if not user.has_perm("employee.can_approve_leave_applications"):
            if self.data.get(
                "applied_leave_type"
            ) == "emergency_leave" and self.has_emergency_leave_last_3_months(
                user.employee
            ):
                raise ValidationError(
                    "You can't apply emergency leave more than 1 in last 3 months"
                )
            if (
                self.data.get("start_date") is not None
                and self.data.get("end_date") is not None
            ):
                start_date = datetime.datetime.strptime(
                    self.data.get("start_date"), "%Y-%m-%d"
                ).date()
                if self.data.get("applied_leave_type") == "casual":
                    if start_date == date.today():
                        raise ValidationError(
                            "You have to apply casual leave before 1 day of start date"
                        )
                    if start_date < date.today():
                        raise ValidationError(
                            "You can not apply any leave past date. You have to apply for emergency or non paid leave"
                        )
                    if (
                        self.data.get("applied_leave_type")
                        not in ["half_day", "half_day_medical"]
                        and (start_date - date.today()).days == 1
                        and time(18, 0) < datetime.datetime.now().time()
                        and not user.has_perm("employee.can_add_leave_at_any_time")
                    ):
                        raise ValidationError(
                            {
                                "start_date": "You can not apply any leave application after 06:00 PM for tomorrow."
                            }
                        )
        return super().clean()

    # def __init__(self, *args, **kwargs):
    #     super(LeaveForm, self).__init__(*args, **kwargs)
    #     if self.fields.get("message"):
    #         self.fields["message"].initial = self.placeholder


@admin.register(Leave)
class LeaveManagement(admin.ModelAdmin):
    actions = ("approve_selected",)
    readonly_fields = ("note", "total_leave")
    exclude = ["status_changed_at", "status_changed_by"]
    inlines = (
        LeaveAttachmentInline,
        LeaveManagementInline,
        FeedbackInline,
    )
    search_fields = ("employee__full_name", "leave_type")
    form = LeaveForm
    date_hierarchy = "start_date"
    fields = (
        "start_date",
        "end_date",
        "applied_leave_type",
        "leave_type",
        "status",
        "employee",
        "message",
        "total_leave",
        "note",
    )

    class Media:
        js = ("js/list.js", "employee/js/leave.js")

    def get_list_display(self, request):
        # existing_list = super(LeaveManagement, self).get_list_display(request)
        list_display = [
            "employee",
            "leave_info",
            "applied_leave_type_",
            "approved_leave_type_",
            "total_leave_",
            "manager_approval",
            "status_",
            # "attachment_link",
            # "get_massage",
            "date_range",
        ]
        if not request.user.has_perm("employee.view_leavefeedback"):
            if "management__feedback" in list_display:
                list_display.remove("management__feedback")
        return list_display

    def get_fields(self, request, obj=None):
        fields = super(LeaveManagement, self).get_fields(request)
        fields = list(fields)
        if not request.user.has_perm("employee.can_approve_leave_applications"):
            admin_only = ["status", "employee", "leave_type"]
            for filed in admin_only:
                fields.remove(filed)
        # if not request.user.has_perm("employee.can_view_feedback"):
        #     fields.remove("display_feedback")
        #     print(fields)
        return fields

    def get_form(self, request, obj=None, change=None, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.request = request
        if form.base_fields.get(
            "applied_leave_type", None
        ) and not request.user.has_perm("employee.can_approve_leave_applications"):
            form.base_fields["applied_leave_type"].label = "Leave Type"
            form.base_fields["applied_leave_type"].required = True
        return form

    @admin.display()
    def status_(self, leave: Leave):
        # Get attachment of leave
        attachments = leave.leaveattachment_set.all()
        if attachments:
            attch_url = attachments[0].attachment.url
        else:
            attch_url = ""

        data = ""
        html_template = get_template("admin/leave/list/col_leave_day.html")

        if leave.status == "pending":
            data = "⏳"
        elif leave.status == "approved":
            data = "✅"
        elif leave.status == "rejected":
            data = "⛔"
        else:
            data = "🤔"

        html_content = html_template.render(
            {
                # 'use_get_display':True,
                "data": data,
                "atch_url": attch_url,
                "message": leave.message,
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

    # def get_massage(self, obj):
    #     return format_html('<span title="{}">📩</span>', obj.message)

    # get_massage.short_description = "Message"

    # def attachment_link(self, obj):
    #     # Check if there are attachments
    #     attachments = obj.leaveattachment_set.all()

    #     if attachments:
    #         # Use the first attachment's URL
    #         url = attachments[0].attachment.url
    #         return format_html(
    #             '<a href="{}" target="_blank" style="color: black;">&#x1F4C4;</a> </br></br>'
    #             '<span title="{}">📩</span>',url, obj.message
    #         )
    #     else:
    #         # Return an icon for no attachment with black color
    #         return '' # Document icon (no attachment)

    # attachment_link.short_description = "Attachments"

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
            # else:
            #     return self.readonly_fields
            elif request.user.employee == obj.employee:
                return ["total_leave", "note"]
            elif (
                request.user.has_perm("employee.can_approve_leave_applications")
                and obj.status == "pending"
                and not request.user.is_superuser
            ):
                return ["applied_leave_type", "total_leave", "note"]
            else:
                return ["total_leave", "note"]
        return ["total_leave", "note"]

    # def save_form(self, request, form, change):
    #     if request._files.get('leaveattachment_set-0-attachment') is None and request._post.get('leave_type') == 'medical':
    #         raise ValidationError({"leaveattachment_set-TOTAL_FORMS":"Attachment is mandatory."})
    #
    #     return super().save_form(request, form, change)

    def save_model(self, request, obj, form, change):
        if not obj.employee_id:
            obj.employee_id = request.user.employee.id

        # Update status change information for users with the necessary permissions
        if request.user.has_perm("employee.can_approve_leave_applications"):
            obj.status_changed_by = request.user
            obj.status_changed_at = date.today()

        # Save the leave object first
        super().save_model(request, obj, form, change)

        employee = form.cleaned_data.get("employee") or request.user.employee

        # Check if this is a new leave or an update
        if not change:
            # For new leaves, assign a manager based on the employee's projects
            projects = EmployeeProject.objects.get(employee=employee)
            project_obj = EmployeeProject.objects.filter(
                project__in=projects.project.all(), employee__active=True
            )
            from django.db.models import Q

            tpm = (
                project_obj.filter(Q(employee__is_tpm=True))
                .exclude(employee__id=employee.id)
                .distinct()
            )
            if tpm.exists():
                leave_manage = leave.LeaveManagement(
                    manager=tpm.first().employee, leave=obj
                )
                leave_manage.save()
            # else:
            #     managers = (
            #         project_obj.filter(Q(employee__manager=True) | Q(employee__lead=True))
            #         .exclude(employee__id=employee.id)
            #         .distinct()
            #     )
            #     for manager in managers:
            #         leave_manage = leave.LeaveManagement(
            #             manager=manager.employee, leave=obj
            #         )
            #         leave_manage.save()

        # Send the email after saving the leave (for both new and updated leaves)
        self.__send_leave_mail(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # Get the Leave instance before calling super().save_related
        leave_instance = form.instance

        # Get the latest feedback for the leave instance from the database directly
        try:
            original_feedback_instance = leave.LeaveFeedback.objects.filter(
                leave=leave_instance
            ).latest("id")
            old_feedback = original_feedback_instance.feedback
        except leave.LeaveFeedback.DoesNotExist:
            old_feedback = None  # No existing feedback, probably a new Leave instance

        # Call the superclass to handle the saving of formsets
        super().save_related(request, form, formsets, change)

        # Now, check if the user is not the employee themselves
        if request.user.employee != leave_instance.employee:
            for formset in formsets:
                if formset.model == leave.LeaveFeedback:
                    for inline_form in formset.cleaned_data:
                        # Get the new feedback from the formset after it's saved
                        new_feedback = inline_form.get("feedback")
                        status = form.cleaned_data.get("status")

                        # Compare the original feedback with the new feedback
                        if old_feedback != new_feedback:
                            self.send_feedback_email(
                                leave_instance, new_feedback, status
                            )

    def send_feedback_email(self, leave_instance, feedback, status):
        subject = "Feedback on your leave application"
        recipient_email = leave_instance.employee.email
        message_content = (
            f"Dear {leave_instance.employee.full_name},\n\n"
            f"Feedback on your leave: {feedback}\n"
            f"Leave Status: {status}\n\n"
            f"Best regards,\nHR Department"
        )
        from_email = '"Mediusware-HR" <hr@mediusware.com>'
        email = EmailMessage(
            subject, message_content, from_email=from_email, to=[recipient_email]
        )
        email.send()

    def has_add_permission(self, request):
        current_datetime = datetime.datetime.now()
        current_day = current_datetime.weekday()

        if not request.user.has_perm("employee.can_add_leave_at_any_time"):
            if current_day in [5, 6]:
                return False
            else:
                return True
        else:
            return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm("employee.can_update_after_approve"):
            return True
        return obj and obj.status == "pending"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("employee.can_approve_leave_applications"):
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ["status", "applied_leave_type", "leave_type", "employee", "start_date"]
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

    @admin.display(description="Applied Leave Type", ordering="applied_leave_type")
    def applied_leave_type_(self, leave: Leave):
        html_template = get_template("admin/leave/list/col_leave_day.html")
        html_content = html_template.render(
            {
                # 'use_get_display':True,
                "data": leave.get_applied_leave_type_display(),
                "leave_day": leave.end_date.strftime("%A"),
                "has_friday": has_friday_between_dates(
                    leave.start_date, leave.end_date
                ),
                "has_monday": leave.applied_leave_type == "emergency_leave",
            }
        )
        return format_html(html_content)

    @admin.display(description="Approved Leave Type", ordering="leave_type")
    def approved_leave_type_(self, leave: Leave):
        html_template = get_template("admin/leave/list/col_leave_day.html")
        html_content = html_template.render(
            {
                # 'use_get_display':True,
                "data": leave.get_leave_type_display(),
                "leave_day": leave.end_date.strftime("%A"),
                "has_friday": has_friday_between_dates(
                    leave.start_date, leave.end_date
                ),
                "has_monday": leave.applied_leave_type == "emergency_leave",
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
                "has_monday": leave.applied_leave_type == "emergency_leave",
            }
        )
        return format_html(html_content)

    change_form_template = "admin/leave/leave_change_form.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        current_time = datetime.datetime.now()
        leave = None
        all_leaves = None
        employee_name = None
        if object_id:
            leave = get_object_or_404(Leave, id=object_id)
            if request.user.employee != leave.employee:
                all_leaves = (
                    Leave.objects.filter(
                        employee=leave.employee, created_at__year=current_time.year
                    )
                    .exclude(id=object_id)
                    .order_by("-id")
                )
                employee_name = leave.employee.full_name
            else:
                all_leaves = Leave.objects.none()
        else:
            all_leaves = Leave.objects.none()

        extra_context = extra_context or {}
        extra_context["all_leaves"] = all_leaves
        extra_context["employee_name"] = employee_name

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

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
    # 'Date (start/end)'

    @admin.display(
        description=format_html(
            '<div style="display: block;">Date</div> <div style="display: block;"><small><u>start</u></small></div> <div style="display: block;"><small>end</small></div> '
        )
    )
    def date_range(self, leave: Leave):
        start_date = leave.start_date.strftime("%Y-%m-%d")
        end_date = leave.end_date.strftime("%Y-%m-%d")
        return format_html(
            '<div style="display: block;">{}</div><div style="display: block;">{}</div>',
            start_date,
            end_date,
        )


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
