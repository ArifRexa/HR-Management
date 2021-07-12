from django.contrib import admin
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.utils.html import format_html

from account.models import Income


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('project', 'hours', 'hour_rate', 'payment_details', 'date', 'status_col')
    date_hierarchy = 'date'
    readonly_fields = ('payment',)
    list_filter = ('status', 'project', 'hour_rate', 'date')

    change_list_template = 'admin/income/list.html'

    def status_col(self, obj):
        color = 'red'
        if obj.status == 'approved':
            color = 'green'
        return format_html(
            f'<b style="color: {color}">{obj.get_status_display()}</b>'
        )

    def payment_details(self, obj):
        return format_html(
            f"<b style='color: green; font-size: 16px'>$ {obj.payment / 80}</b> / "
            f"{obj.payment} TK"
        )

    def get_total_hour(self, request):
        filters = dict([(key, request.GET.get(key)) for key in dict(request.GET) if key not in ['p', 'o']])
        if not request.user.is_superuser:
            filters['created_by__id__exact'] = request.user.employee.id
        dataset = Income.objects.filter(*[Q(**{key: value}) for key, value in filters.items() if value])
        return {
            'total_pending': dataset.filter(status='pending').aggregate(total=Coalesce(Sum('payment'), 0.0))['total'],
            'total_paid': dataset.filter(status='approved').aggregate(total=Coalesce(Sum('payment'), 0.0))['total'],
            'pending_hour': dataset.filter(status='pending').aggregate(total=Coalesce(Sum('hours'), 0.0))['total'],
            'approved_hour': dataset.filter(status='approved').aggregate(total=Coalesce(Sum('hours'), 0.0))['total'],
        }

    def changelist_view(self, request, extra_context=None):
        my_context = {
            'result': self.get_total_hour(request),
        }
        return super().changelist_view(request, extra_context=my_context)
