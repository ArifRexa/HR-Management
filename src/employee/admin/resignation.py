from datetime import date

from django_q.tasks import async_task
from django.contrib import admin
from config.admin import RecentEdit
from employee.models import Resignation
from employee.models.resignation import ResignationFeedback
from django.template import loader


class ResignationFeedbackInline(admin.TabularInline):
    model = ResignationFeedback
    extra = 0
    fields = ["message", "feedback_created_by"]

    def get_readonly_fields(self, request, obj=None):
        # if obj and obj.created_by != request.user:
        #     return ["feedback_created_by", "message"]
        return ["feedback_created_by"]

    @admin.display(description="Created By")
    def feedback_created_by(self, obj):
        return obj.created_by if obj.created_by else "-"

    # def has_delete_permission(self, request, obj=None):
    #     if not obj:
    #         return super().has_delete_permission(request, obj)
    #     return request.user.is_superuser or request.user == obj.created_by

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Resignation)
class ResignationAdmin(RecentEdit, admin.ModelAdmin):
    list_display = (
        "employee",
        "short_message",
        "date",
        "status",
        "approved_at",
        "approved_by",
    )
    search_fields = ["employee__full_name", "message"]
    inlines = [ResignationFeedbackInline]

    def get_fields(self, request, obj=None):
        fields = super(ResignationAdmin, self).get_fields(request)
        if not request.user.has_perm("employee.can_view_all_resignations"):
            fields.remove("employee")
            fields.remove("status")
        return fields

    def get_queryset(self, request):
        qs = super(ResignationAdmin, self).get_queryset(request)
        if request.user.has_perm("employee.can_view_all_resignations"):
            return qs
        return qs.filter(employee_id=request.user.employee)

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser or request.user.has_perm(
            "employee.can_view_all_resignations"
        ):
            obj.approved_at = date.today()
            obj.approved_by = request.user
        else:
            obj.employee = request.user.employee
        is_resignation_creating = not obj.pk
        super().save_model(request, obj, form, change)
        if is_resignation_creating:
            async_task(
                "employee.tasks.send_resignation_application_email",
                obj,
            )

    def has_module_permission(self, request):
        return False

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for inline_form in formset.forms:
                if (
                    inline_form._meta.model == ResignationFeedback
                    and inline_form.instance.id is None
                    and inline_form.cleaned_data
                ):
                    resignation = inline_form.cleaned_data.get("resignation")
                    feedback = inline_form.cleaned_data.get("message")
                    if request.user.employee != resignation.employee:
                        subject = "Feedback on Your Resignation From Mediusware Ltd."
                        recipient_email = [resignation.employee.email]
                        from_email = '"Mediusware-HR" <hr@mediusware.com>'
                        
                        body = loader.render_to_string(
                            "mails/resignation_feedback.html",
                            context={
                                "greet_name": resignation.employee.full_name,
                                "feedback": feedback,
                                "best_regards": "MD Shahjahan Kabir",
                                "contact_email": "hr@mediusware.com",
                            },
                        )
                    else:
                        subject = f"Feedback For Resignation From {resignation.employee.full_name}"
                        recipient_email = ['<hr@mediusware.com>']
                        from_email = resignation.employee.email
                        body = loader.render_to_string(
                            "mails/resignation_feedback.html",
                            context={
                                "greet_name": resignation.employee.full_name,
                                "feedback": feedback,
                                "best_regards": resignation.employee.full_name,
                                "contact_email": resignation.employee.email,
                            },
                        )
                    async_task(
                        "employee.tasks.send_resignation_feedback_email",
                        subject,
                        body,
                        from_email,
                        recipient_email,
                    )
        return super().save_related(request, form, formsets, change)
