from datetime import date

from django.contrib import admin, messages
from django import forms
from django.template.loader import get_template
from django.utils.html import format_html
from django_q.tasks import async_task

from employee.models import LeaveAttachment, Leave


class LeaveAttachmentInline(admin.TabularInline):
    model = LeaveAttachment
    extra = 0


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
        widget=forms.Textarea(attrs={'placeholder': placeholder, 'cols': 100, 'rows': 15})
    )

    class Meta:
        model = Leave
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(LeaveForm, self).__init__(*args, **kwargs)
        if self.fields.get('message'):
            self.fields['message'].initial = self.placeholder


@admin.register(Leave)
class LeaveManagement(admin.ModelAdmin):
    list_display = ('employee', 'leave_info', 'leave_type', 'total_leave',
                    'status', 'start_date', 'end_date')
    actions = ('approve_selected',)
    readonly_fields = ('note', 'total_leave')
    exclude = ['status_changed_at', 'status_changed_by']
    inlines = (LeaveAttachmentInline,)
    search_fields = ('employee__full_name', 'leave_type')
    form = LeaveForm
    date_hierarchy = 'start_date'

    def get_fields(self, request, obj=None):
        fields = super(LeaveManagement, self).get_fields(request)
        if not request.user.has_perm("employee.can_approve_leave_applications"):
            admin_only = ['status', 'employee']
            for filed in admin_only:
                fields.remove(filed)
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            leave = Leave.objects.filter(id=request.resolver_match.kwargs['object_id']).first()
            if not leave.status == 'pending' and not request.user.has_perm("employee.can_approve_leave_applications"):
                return self.readonly_fields + tuple([item.name for item in obj._meta.fields])
        return ['total_leave', 'note']

    def save_model(self, request, obj, form, change):
        if not obj.employee_id:
            obj.employee_id = request.user.employee.id
        if request.user.has_perm("employee.can_approve_leave_applications"):
            obj.status_changed_by = request.user
            obj.status_changed_at = date.today()
        super().save_model(request, obj, form, change)
        self.__send_leave_mail(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("employee.can_approve_leave_applications"):
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ['status', 'leave_type', 'employee', 'start_date']
        if not request.user.has_perm("employee.can_approve_leave_applications"):
            list_filter.remove('employee')
        return list_filter

    def __send_leave_mail(self, request, obj, form, change):
        if len(form.changed_data) > 0 and 'status' in form.changed_data:
            async_task('employee.tasks.leave_mail', obj)
        elif not change:
            async_task('employee.tasks.leave_mail', obj)

    @admin.action()
    def approve_selected(self, request, queryset):
        if (
            request.user.is_superuser 
            or request.user.has_perm("employee.can_approve_leave_applications")
        ):
            messages.success(request, 'Leaves approved.')
            queryset.update(status='approved')
        else:
            messages.error(request, 'You don\' have permission.')


    @admin.display()
    def leave_info(self, leave: Leave):
        year_end_date = leave.end_date.replace(month=12, day=31)

        html_template = get_template('admin/leave/list/col_leave_info.html')
        html_content = html_template.render({
            'casual_passed': leave.employee.leave_passed('casual', year_end_date.year),
            'casual_remain': leave.employee.leave_available('casual_leave', year_end_date),
            'medical_passed': leave.employee.leave_passed('medical', year_end_date.year),
            'medical_remain': leave.employee.leave_available('medical_leave', year_end_date),
        })
        return format_html(html_content)
