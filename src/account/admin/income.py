from django.contrib import admin, messages
from django.db import models
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce
from django.forms import Textarea
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html

from account.models import Income
from account.services.balance import BalanceSummery


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('project', 'date', 'hours', 'hour_rate', 'payment_details', 'status_col')
    date_hierarchy = 'date'
    readonly_fields = ('payment',)
    list_filter = ('status', 'project', 'hour_rate', 'date')
    actions = ['approve_selected', 'pending_selected']
    # list_editable = ('status',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2})}
    }

    change_list_template = 'admin/income/list.html'

    list_per_page = 20

    @admin.action(description='Status')
    def status_col(self, obj):
        color = 'red'
        if obj.status == 'approved':
            color = 'green'
        return format_html(
            f'<b style="color: {color}">{obj.get_status_display()}</b>'
        )

    @admin.display()
    def payment_details(self, obj):
        return format_html(
            f"<b style='color: green; font-size: 16px'>$ {obj.payment / obj.convert_rate}</b> / "
            f"{obj.payment} TK"
        )

    def get_total_hour(self, request):
        filters = dict([(key, request.GET.get(key)) for key in dict(request.GET) if key not in ['p', 'o']])
        if not request.user.is_superuser:
            filters['created_by__id__exact'] = request.user.employee.id
        dataset = Income.objects.filter(*[Q(**{key: value}) for key, value in filters.items() if value])
        return {
            'total_pending': dataset.filter(status='pending').aggregate(total=Coalesce(Sum('payment'), 0.0))['total'],
            'total_pending_usd': dataset.filter(status='pending').aggregate(
                total=Coalesce(Sum(F('payment') / F('convert_rate')), 0.0))['total'],
            'total_paid': dataset.filter(status='approved').aggregate(total=Coalesce(Sum('payment'), 0.0))['total'],
            'total_paid_usd': dataset.filter(status='approved').aggregate(
                total=Coalesce(Sum(F('payment') / F('convert_rate')), 0.0))['total'],
            'pending_hour': dataset.filter(status='pending').aggregate(total=Coalesce(Sum('hours'), 0.0))['total'],
            'approved_hour': dataset.filter(status='approved').aggregate(total=Coalesce(Sum('hours'), 0.0))['total'],
        }

    def changelist_view(self, request, extra_context=None):
        my_context = {
            'result': self.get_total_hour(request),
        }
        return super().changelist_view(request, extra_context=my_context)

    @admin.action()
    def approve_selected(self, request, queryset):
        queryset.update(status='approved')
        # self.message_user(request, f'Status has been updated to approved for {len(queryset)} items', messages.SUCCESS)

    @admin.action()
    def pending_selected(self, request, queryset):
        queryset.update(status='pending')
        # self.message_user(request, f'Status has been updated to pending for {len(queryset)} items', messages.SUCCESS)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('balance/', self.admin_site.admin_view(self.balance_view), name='account_balance'),
        ]
        return my_urls + urls

    def balance_view(self, request, *args, **kwargs):
        if request.user.is_superuser:
            balance = (BalanceSummery()).get_context_data()
            context = dict(
                self.admin_site.each_context(request),
                data=balance,
                title=f'Profit / Loss'
            )
            return TemplateResponse(request, "admin/balance/balance.html", context)
        raise PermissionDenied
