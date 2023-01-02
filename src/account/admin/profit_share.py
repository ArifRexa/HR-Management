from django.contrib import admin
from django.db.models import Sum

from account.models import ProfitShare
from config.admin.utils import simple_request_filter


@admin.register(ProfitShare)
class ProfitShareAdmin(admin.ModelAdmin):
    list_display = ('date', 'payment_amount', 'note', 'user')
    date_hierarchy = 'date'
    change_list_template = 'admin/profit_share/list.html'

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        extra_context = {
            'total': qs.aggregate(tot=Sum('payment_amount'))['tot']
        }
        return super(ProfitShareAdmin, self).changelist_view(request, extra_context)
    
    def has_module_permission(self, request):
        return False
