from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.core.exceptions import PermissionDenied

from account.models import Expense, Fund, FundCategory
from config.admin import RecentEdit
from employee.models import Employee


@admin.register(FundCategory)
class FundCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')
    search_fields = ['title']

    def has_module_permission(self, request):
        return False


@admin.register(Fund)
class FundAdmin(RecentEdit, admin.ModelAdmin):
    list_display = ['date', 'amount', 'user_full_name', 'note', 'get_fund', 'status']
    list_filter = ['status', 'date', 'user']
    autocomplete_fields = ['user', 'fund_category']

    @admin.display(description='User')
    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    @admin.display(description='Current Fund')
    def get_fund(self, obj):
        # Access the user associated with the Fund instance
        user = obj.user
        # Calculate total funds added for the user
        fund_added = user.fund_set.aggregate(total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
        # Calculate total expenses approved by the user
        fund_subtract = Expense.objects.filter(approved_by=user).aggregate(
            total_amount=Coalesce(Sum('amount'), 0.0))['total_amount']
        return fund_added - fund_subtract

    def get_readonly_fields(self, request, obj=None):
        # If the Fund object exists and its status is 'approved', make 'amount' read-only
        if obj and obj.status == 'approved':
            return ['amount'] + list(self.readonly_fields)  # Convert tuple to list
        return list(self.readonly_fields)  # Ensure a list is returned

    def has_change_permission(self, request, obj=None):
        # Allow superusers to change any Fund object
        if request.user.is_superuser:
            return True
        # For non-superusers, prevent changing the status to 'approved'
        if obj and obj.status == 'approved':
            return False  # Prevent non-superusers from editing approved funds
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change) -> None:
        # Check if status is being changed to 'approved' and ensure only superusers can do this
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
    