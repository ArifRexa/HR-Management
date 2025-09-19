from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.contrib import messages
from django.contrib.admin import SimpleListFilter

from account.models import Expense, Fund, FundCategory, AssistantFund
from config.admin import RecentEdit
from employee.models import Employee


@admin.register(FundCategory)
class FundCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')
    search_fields = ['title']

    def has_module_permission(self, request):
        return False


# @admin.register(Fund)
# class FundAdmin(RecentEdit, admin.ModelAdmin):
#     list_display = ['date', 'amount', 'user_full_name', 'note', 'fund_category', 'get_fund', 'status']
#     list_filter = ['status', 'date', 'user']
#     autocomplete_fields = ['user', 'fund_category']

#     @admin.display(description='User')
#     def user_full_name(self, obj):
#         return f"{obj.user.first_name} {obj.user.last_name}".strip()

#     @admin.display(description='Current Fund')
#     def get_fund(self, obj):
#         # Access the user associated with the Fund instance
#         user = obj.user
#         # Calculate total funds added for the user
#         fund_added = user.fund_set.aggregate(total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
#         # Calculate total expenses approved by the user
#         fund_subtract = Expense.objects.filter(approved_by=user).aggregate(
#             total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
#         return fund_added - fund_subtract

#     def get_readonly_fields(self, request, obj=None):
#         # If the Fund object exists and its status is 'approved', make 'amount' read-only
#         if obj and obj.status == 'approved':
#             return ['amount'] + list(self.readonly_fields)  # Convert tuple to list
#         return list(self.readonly_fields)  # Ensure a list is returned

#     def has_change_permission(self, request, obj=None):
#         # Allow superusers to change any Fund object
#         if request.user.is_superuser:
#             return True
#         # For non-superusers, prevent changing the status to 'approved'
#         if obj and obj.status == 'approved':
#             return False  # Prevent non-superusers from editing approved funds
#         return super().has_change_permission(request, obj)

#     def save_model(self, request, obj, form, change) -> None:
#         # Check if status is being changed to 'approved' and ensure only superusers can do this
#         if change and 'status' in form.changed_data and obj.status == 'approved' and not request.user.is_superuser:
#             raise PermissionDenied("Only superusers can approve funds.")
        
#         employee = Employee.objects.get(user=obj.user)

#         html_template = get_template('mail/fund_mail.html')
#         html_content = html_template.render({
#             'fund': obj,
#             'employee': employee
#         })

#         email = EmailMultiAlternatives(subject=f'Fund Added on {obj.date.strftime("%b %d, %Y")}')
#         email.attach_alternative(html_content, 'text/html')
#         email.to = [employee.email]
#         email.from_email = 'admin@mediusware.com'
        
#         email.send()

#         return super().save_model(request, obj, form, change)
    



# @admin.register(Fund)
# class FundAdmin(RecentEdit, admin.ModelAdmin):
#     list_display = ['date', 'amount', 'user_full_name', 'note', 'fund_category', 'get_fund', 'status']
#     list_filter = ['status', 'date', 'user']
#     autocomplete_fields = ['user', 'fund_category']
    
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if not request.user.is_superuser:
#             return qs.filter(user=request.user)
#         return qs

#     def get_exclude(self, request, obj=None):
#         excluded = super().get_exclude(request, obj) or []
#         if not request.user.is_superuser:
#             return excluded + ['user']
#         return excluded

#     def save_model(self, request, obj, form, change):
#         if not change and not request.user.is_superuser:
#             obj.user = request.user
            
#         # Existing save_model logic continues here
#         if change and 'status' in form.changed_data and obj.status == 'approved' and not request.user.is_superuser:
#             raise PermissionDenied("Only superusers can approve funds.")
        
#         employee = Employee.objects.get(user=obj.user)
#         html_template = get_template('mail/fund_mail.html')
#         html_content = html_template.render({
#             'fund': obj,
#             'employee': employee
#         })
#         email = EmailMultiAlternatives(subject=f'Fund Added on {obj.date.strftime("%b %d, %Y")}')
#         email.attach_alternative(html_content, 'text/html')
#         email.to = [employee.email]
#         email.from_email = 'admin@mediusware.com'
#         email.send()
#         return super().save_model(request, obj, form, change)

#     # Keep all existing methods unchanged
#     @admin.display(description='User')
#     def user_full_name(self, obj):
#         return f"{obj.user.first_name} {obj.user.last_name}".strip()
    
#     @admin.display(description='Current Fund')
#     def get_fund(self, obj):
#         user = obj.user
#         fund_added = user.fund_set.aggregate(total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
#         fund_subtract = Expense.objects.filter(approved_by=user).aggregate(
#             total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
#         return fund_added - fund_subtract
    
#     def get_readonly_fields(self, request, obj=None):
#         if obj and obj.status == 'approved':
#             return ['amount'] + list(self.readonly_fields)
#         return list(self.readonly_fields)
    
#     def has_change_permission(self, request, obj=None):
#         if request.user.is_superuser:
#             return True
#         if obj and obj.status == 'approved':
#             return False
#         return super().has_change_permission(request, obj)


class FundUserFilter(SimpleListFilter):
    title = 'user'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        # Get users who have created funds
        users = Fund.objects.values_list('user', 'user__first_name', 'user__last_name').distinct()
        return [(user[0], f"{user[1]} {user[2]}".strip()) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id=self.value())
        return queryset

class AssistantFundUserFilter(FundUserFilter):
    def lookups(self, request, model_admin):
        # Get users who have created funds
        users = AssistantFund.objects.values_list('user', 'user__first_name', 'user__last_name').distinct()
        return [(user[0], f"{user[1]} {user[2]}".strip()) for user in users]


@admin.register(Fund)
class FundAdmin(RecentEdit, admin.ModelAdmin):
    list_display = ['date', 'amount', 'user_full_name', 'note', 'fund_category', 'get_fund', 'colored_status']
    list_filter = ['status', 'date',  FundUserFilter]
    autocomplete_fields = ['user', 'fund_category']
    actions = ['approve_selected_funds']


    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove the approve action for non-superusers
        if not request.user.is_superuser and 'approve_selected_funds' in actions:
            del actions['approve_selected_funds']
        return actions


    @admin.display(description='Status')
    def colored_status(self, obj):
        if obj.status == 'approved':
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', obj.get_status_display())
        elif obj.status == 'pending':
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', obj.get_status_display())
        return obj.get_status_display()
    
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     if not request.user.is_superuser:
    #         return qs.filter(user=request.user)
    #     return qs
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or self._has_user_permission(request):
            return qs
        return qs.filter(user=request.user)

    # def get_exclude(self, request, obj=None):
    #     excluded = super().get_exclude(request, obj) or []
    #     if not request.user.is_superuser:
    #         return excluded + ['user']
    #     return excluded
    def get_exclude(self, request, obj=None):
        excluded = super().get_exclude(request, obj) or []
        
        # Only exclude 'user' field if user doesn't have permission
        if not request.user.is_superuser and not self._has_user_permission(request):
            excluded.append('user')
            
        return excluded

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj) or [])
        
        # Make amount read-only for approved funds
        if obj and obj.status == 'approved':
            readonly_fields.append('amount')
            
        # For non-superusers, make status read-only
        if not request.user.is_superuser:
            readonly_fields.append('status')
            
        return readonly_fields

    # def save_model(self, request, obj, form, change):
    #     if not change and not request.user.is_superuser:
    #         obj.user = request.user
            
    #     # Check if status is being changed to 'approved' by non-superuser
    #     if change and 'status' in form.changed_data and obj.status == 'approved' and not request.user.is_superuser:
    #         raise PermissionDenied("Only superusers can approve funds.")
    def save_model(self, request, obj, form, change):
        # Only set user automatically for non-permitted users
        if not change and not request.user.is_superuser and not self._has_user_permission(request):
            obj.user = request.user
            
        # Check if status is being changed to 'approved' by non-superuser
        if change and 'status' in form.changed_data and obj.status == 'approved' and not request.user.is_superuser:
            raise PermissionDenied("Only superusers can approve funds.")
        
        employee = Employee.objects.get(user=obj.user)
        html_template = get_template('mail/fund_mail.html')
        html_content = html_template.render({
            'fund': obj,
            'employee': employee
        })
        email = EmailMultiAlternatives(subject=f'Fund Added on {obj.date.strftime("%b %d, %Y")}')
        email.attach_alternative(html_content, 'text/html')
        email.to = [employee.email]
        email.from_email = 'admin@mediusware.com'
        email.send()
        return super().save_model(request, obj, form, change)

    # Keep all existing methods unchanged
    @admin.display(description='User')
    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    
    # @admin.display(description='Current Fund')
    # def get_fund(self, obj):
    #     user = obj.user
    #     fund_added = user.fund_set.aggregate(total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
    #     fund_subtract = Expense.objects.filter(approved_by=user).aggregate(
    #         total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
    #     return fund_added - fund_subtract
    @admin.display(description='Current Fund')
    def get_fund(self, obj):
        user = obj.user
        # Calculate total approved funds added for the user
        fund_added = user.fund_set.filter(status='approved').aggregate(
            total_amount=Coalesce(Sum('amount'), 0.0)
        )['total_amount']
        # Calculate total expenses approved by the user
        fund_subtract = Expense.objects.filter(approved_by=user).aggregate(
            total_amount=Coalesce(Sum('amount'), 0.0)
        )['total_amount']
        return fund_added - fund_subtract
    
    # def has_change_permission(self, request, obj=None):
    #     # Superusers can change any fund
    #     if request.user.is_superuser:
    #         return True
            
    #     # Non-superusers can only change their own pending funds
    #     if obj:
    #         return obj.user == request.user and obj.status == 'pending'
    #     return super().has_change_permission(request, obj)
    def has_change_permission(self, request, obj=None):
        # Superusers can change any fund
        if request.user.is_superuser:
            return True
            
        if self._has_user_permission(request):
            return True
            
        if obj:
            return obj.user == request.user and obj.status == 'pending'
        return super().has_change_permission(request, obj)
    
    def _has_user_permission(self, request):
        """Check if user has permission to view/change fund user"""
        return (request.user.has_perm('account.view_fund_user') or 
                request.user.has_perm('account.change_fund_user'))
    
    @admin.action(description='Approve selected funds')
    def approve_selected_funds(self, request, queryset):
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can approve funds.")
        
        # Count how many funds we're approving
        count = 0
        approved_funds = []
        
        # Process each fund in the queryset
        for fund in queryset:
            # Only approve if it's not already approved
            if fund.status != 'approved':
                fund.status = 'approved'
                fund.save()
                count += 1
                approved_funds.append(fund)
                
                # Send approval email
                employee = Employee.objects.get(user=fund.user)
                html_template = get_template('mail/fund_mail.html')
                html_content = html_template.render({
                    'fund': fund,
                    'employee': employee
                })
                email = EmailMultiAlternatives(
                    subject=f'Fund Approved on {fund.date.strftime("%b %d, %Y")}'
                )
                email.attach_alternative(html_content, 'text/html')
                email.to = [employee.email]
                email.from_email = 'admin@mediusware.com'
                email.send()
        
        # Display success message
        if count > 0:
            self.message_user(
                request, 
                f"Successfully approved {count} fund{'s' if count != 1 else ''}.",
                messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                "No funds were approved (they may already be approved).",
                messages.WARNING
            )

@admin.register(AssistantFund)
class AssistantFundAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'user_full_name', 'note', 'fund_category', 'get_fund', 'colored_status']
    list_filter = ['status', 'date',  AssistantFundUserFilter]
    autocomplete_fields = ['user', 'fund_category']
    actions = ['approve_selected_funds']

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove the approve action for non-permitede
        if 'approve_selected_funds' in actions and not request.user.has_perm("account.approve_assistant_fund_status"):
            del actions['approve_selected_funds']
        return actions


    @admin.display(description='Status')
    def colored_status(self, obj):
        if obj.status == 'approved':
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', obj.get_status_display())
        elif obj.status == 'pending':
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', obj.get_status_display())
        return obj.get_status_display()


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.has_perm('account.view_assistant_fund_user'):
            return qs
        return qs.filter(user=request.user)

    
    def get_exclude(self, request, obj=None):
        excluded = super().get_exclude(request, obj) or []
        
        # Only exclude 'user' field if user doesn't have permission
        if not request.user.has_perm("account.add_assistant_fund_to_user"):
            excluded.append('user')
        return excluded

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj) or [])
        
        # Make amount read-only for approved funds
        if obj and obj.status == 'approved':
            readonly_fields.append('amount')
            
        # For non-superusers, make status read-only
        # if request.user.is_superuser:
        #     return readonly_fields
        elif not request.user.has_perm("account.approve_assistant_fund_status"):
            readonly_fields.append('status')
        return readonly_fields


    def save_model(self, request, obj, form, change):
        # Only set user automatically for non-permitted users
        if not change and not request.user.has_perm("account.add_assistant_fund_to_user"):
            obj.user = request.user
            
        # Check if status is being changed to 'approved' by non-superuser
        # if change and 'status' in form.changed_data and obj.status == 'approved' and not request.user.has_perm("account.approve_assistant_fund_status"):
        #     raise PermissionDenied("Only superusers can approve funds.")
        
        employee = Employee.objects.get(user=obj.user)
        html_template = get_template('mail/fund_mail.html')
        html_content = html_template.render({
            'fund': obj,
            'employee': employee
        })
        email = EmailMultiAlternatives(subject=f'Fund Added on {obj.date.strftime("%b %d, %Y")}')
        email.attach_alternative(html_content, 'text/html')
        email.to = [employee.email]
        email.from_email = 'admin@mediusware.com'
        email.send()
        return super().save_model(request, obj, form, change)

    # Keep all existing methods unchanged
    @admin.display(description='User')
    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    
    @admin.display(description='Current Fund')
    def get_fund(self, obj):
        user = obj.user
        # Calculate total approved funds added for the user
        fund_added = user.assistantfund_set.filter(status='approved').aggregate(
            total_amount=Coalesce(Sum('amount'), 0.0)
        )['total_amount']
        # Calculate total expenses approved by the user
        fund_subtract = Expense.objects.filter(
            is_approved=True,
            created_by=user,
        ).aggregate(
            total_amount=Coalesce(Sum('amount'), 0.0)
        )['total_amount']
        return fund_added - fund_subtract
    
    def has_change_permission(self, request, obj=None):
        # Superusers can change any Assistant Fund
        if request.user.is_superuser:
            return True
        if obj:
            return super().has_change_permission(request, obj) and obj.status == 'pending'
        return super().has_change_permission(request, obj)


    @admin.action(description='Approve selected funds')
    def approve_selected_funds(self, request, queryset):
        if not request.user.has_perm("account.approve_assistant_fund_status"):
            raise PermissionDenied("Only permited user can approve funds.")
        
        # Count how many funds we're approving
        count = 0
        approved_funds = []
        
        # Process each fund in the queryset
        for fund in queryset:
            # Only approve if it's not already approved
            if fund.status != 'approved':
                fund.status = 'approved'
                fund.save()
                count += 1
                approved_funds.append(fund)
                
                # Send approval email
                employee = Employee.objects.get(user=fund.user)
                html_template = get_template('mail/fund_mail.html')
                html_content = html_template.render({
                    'fund': fund,
                    'employee': employee
                })
                email = EmailMultiAlternatives(
                    subject=f'Fund Approved on {fund.date.strftime("%b %d, %Y")}'
                )
                email.attach_alternative(html_content, 'text/html')
                email.to = [employee.email]
                email.from_email = 'admin@mediusware.com'
                email.send()
        
        # Display success message
        if count > 0:
            self.message_user(
                request, 
                f"Successfully approved {count} fund{'s' if count != 1 else ''}.",
                messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                "No funds were approved (they may already be approved).",
                messages.WARNING
            )

    # def _has_user_permission(self, request):
    #     """Check if user has permission to view/change fund user"""
    #     return (
    #             # request.user.has_perm('account.view_assistant_fund_user') or 
    #             request.user.has_perm('account.change_assistant_fund_user') or
    #             request.user.has_perm('account.assistant_fund_superuser')
    #         )
