from django.contrib import admin
from django.db.models import Q, Sum
from django.utils.html import format_html

from account.models import Income


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('project', 'hours', 'hour_rate', 'payment_details', 'date')
    date_hierarchy = 'date'
    readonly_fields = ('payment',)
    list_filter = ('project', 'hour_rate', 'date')

    change_list_template = 'admin/income/list.html'

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
        return dataset.aggregate(tot=Sum('payment'))['tot']

    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super().changelist_view(request, extra_context=my_context)
