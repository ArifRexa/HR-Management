from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Sum, Q

from account.models import Expense, ExpenseCategory, ExpanseAttachment, ExpenseGroup
from config.admin.utils import simple_request_filter


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')


class ExpanseAttachmentInline(admin.TabularInline):
    model = ExpanseAttachment
    extra = 1


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'expanse_group', 'expense_category', 'amount', 'note', 'created_by')
    date_hierarchy = 'date'
    list_filter = ['expanse_group', 'expense_category', 'date']
    change_list_template = 'admin/expense/list.html'
    inlines = [ExpanseAttachmentInline]
    search_fields = ['note']

    def get_queryset(self, request):
        qs = super(ExpenseAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(created_by__id=request.user.id)
        return qs

    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(**simple_request_filter(request))
        if not request.user.is_superuser:
            qs.filter(created_by__id=request.user.id)
        return qs.aggregate(total=Sum('amount'))['total']

    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super().changelist_view(request, extra_context=my_context)
    # TODO : Export to excel
    # TODO : Credit feature
