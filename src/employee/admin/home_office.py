from datetime import date

from django.contrib import admin, messages
from django import forms

from employee.models import (
    HomeOffice, 
    HomeOfficeAttachment,
)


class HomeOfficeAttatchmentInline(admin.TabularInline):
    model = HomeOfficeAttachment
    extra = 0


class HomeOfficeForm(forms.ModelForm):
    placeholder = """Sample application with full explanation
=========================================

Hello sir,

I have huge leg-pain. So I won't be able to join office tomorrow. I'll have to do home office tomorrow.

I ensure that my internet connection is stable and electricity is always available.

I will join office day after tomorrow.

Thank you
[Full Name]
"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': placeholder, 'cols': 100, 'rows': 15})
    )

    class Meta:
        model = HomeOffice
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.fields.get('message'):
            self.fields['message'].initial = self.placeholder


@admin.register(HomeOffice)
class HomeOfficeManagement(admin.ModelAdmin):
    list_display = (
        'employee',
        'total_day',
        'status', 
        'start_date', 
        'end_date',
    )
    actions = ('approve_selected',)
    readonly_fields = ('note', 'total_day',)
    exclude = ['status_changed_at', 'status_changed_by']
    search_fields = ('employee__full_name',)
    date_hierarchy = 'start_date'
    
    inlines = (HomeOfficeAttatchmentInline,)
    form = HomeOfficeForm
    
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request)
        if not request.user.has_perm("employee.can_approve_homeoffice_application"):
            admin_only = ['status', 'employee']
            for filed in admin_only:
                fields.remove(filed)
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            if (
                not obj.status == 'pending'
                and not request.user.has_perm("employee.can_approve_homeoffice_application")
            ):
                return list(self.readonly_fields) + [item.name for item in obj._meta.fields]
        return ['total_day', 'note']
    
    def save_model(self, request, obj, form, change):
        if not obj.employee_id:
            obj.employee_id = request.user.employee.id
        if request.user.has_perm("employee.can_approve_homeoffice_application"):
            obj.status_changed_by = request.user
            obj.status_changed_at = date.today()
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("employee.can_approve_homeoffice_application"):
            return qs
        return qs.filter(employee_id=request.user.employee)

    def get_list_filter(self, request):
        list_filter = ['status', 'employee']
        if not request.user.has_perm("employee.can_approve_homeoffice_application"):
            list_filter.remove('employee')
        return list_filter
    
    @admin.action(description="Approve Selected Applications")
    def approve_selected(self, request, queryset):
        if request.user.has_perm("employee.can_approve_homeoffice_application"):
            messages.success(request, 'Home Office Applications approved.')
            queryset.update(status='approved')
        else:
            messages.error(request, 'You don\' have permission.')

    def has_module_permission(self, request):
        return False