from typing import Optional
from django.contrib import admin, messages
from django.http.request import HttpRequest
from employee.models import BankAccount


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('employee', 'bank', 'default', 'is_approved')
    actions = ('approve_bank_account_info',"make_default")
    list_filter = ('employee',)
    fields = (
        'bank',
        'account_number',
        'default',
    )
    search_fields = (
        'employee__full_name',
        'bank__name',
        'account_number',
    )
    
    @admin.action(description="Make Default Account")
    def make_default(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, "You can only select one bank account to make default")
            return
        queryset.update(default=True)
        messages.success(request, "Default Bank Account Updated")

    def has_module_permission(self, request):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related(
            'employee',
            'bank',
        )
        if (
            request.user.is_superuser
            or request.user.has_perm('employee.can_edit_all_bank_account')
            or request.user.has_perm("employee.can_approve_bank_account_info")
        ):
            return qs
        return qs.filter(employee=request.user.employee)
    
    
    def get_list_filter(self, request):
        if (
            request.user.is_superuser 
            or request.user.has_perm('employee.can_edit_all_bank_account')
            or request.user.has_perm("employee.can_approve_bank_account_info")
        ):
            return super().get_list_filter(request)
        return []
    
    
    def get_fields(self, request, obj):
        fields = super().get_fields(request, obj)

        if (
            request.user.is_superuser 
            or request.user.has_perm("employee.can_edit_all_bank_account")
        ):
            fields = ("employee", *fields,)
        if (
            request.user.is_superuser
            or request.user.has_perm("employee.can_approve_bank_account_info")
        ):
            fields = (*fields, "is_approved")
        
        return fields
    
    
    def save_model(self, request, obj, *args, **kwargs):
        if not obj.employee_id:
            obj.employee_id = request.user.employee.id
        return super().save_model(request, obj, *args, **kwargs)
    
    
    @admin.action(description="Approve Account Info")
    def approve_bank_account_info(self, request, queryset):
        if (
            request.user.is_superuser
            or request.user.has_perm("employee.can_approve_bank_account_info")
        ):
            queryset.update(is_approved=True)
            messages.success(request, "Approve Status Updated")
    
    
    def has_change_permission(self, request, obj=None):
        perm = super().has_change_permission(request, obj) 
        if not request.user.is_superuser:
            if obj:
                if request.user.has_perm("employee.can_edit_all_bank_account"):
                    perm=True
                elif request.user.employee == obj.employee and not obj.is_approved:
                    perm=True
                else:
                    perm=False
            else:
                perm=True
        return perm

