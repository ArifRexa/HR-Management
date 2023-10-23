from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from account.models import Fund, FundCategory
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
    list_display = ['date', 'amount', 'user', 'fund_category', 'note']
    list_filter = ['date', 'user']
    autocomplete_fields = ['user', 'fund_category']

    def save_model(self, request, obj, form, change) -> None:
        employee = Employee.objects.get(user=obj.user)

        html_template = get_template('mail/fund_mail.html')
        html_content = html_template.render({
            'fund': obj,
            'employee':employee
        })

        email = EmailMultiAlternatives(subject=f'Fund Added on {obj.date.strftime("%b %d, %Y")}')
        email.attach_alternative(html_content, 'text/html')
        email.to = [employee.email]
        email.from_email = 'admin@mediusware.com'
        email.send()

        return super().save_model(request, obj, form, change)
    