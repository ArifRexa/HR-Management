from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Sum, Q

from account.models import Expense, ExpenseCategory, ExpanseAttachment


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')


class ExpanseAttachmentInline(admin.TabularInline):
    model = ExpanseAttachment
    extra = 1


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'expense_category', 'amount', 'note', 'created_by')
    date_hierarchy = 'date'
    list_filter = ['expense_category__title', 'date']
    change_list_template = 'admin/expense/list.html'
    inlines = [ExpanseAttachmentInline]

    def get_total_hour(self, request):
        filters = dict([(key, request.GET.get(key)) for key in dict(request.GET) if key not in ['p', 'o']])
        if not request.user.is_superuser:
            filters['created_by__id__exact'] = request.user.employee.id
        dataset = Expense.objects.filter(*[Q(**{key: value}) for key, value in filters.items() if value])
        return dataset.aggregate(tot=Sum('amount'))['tot']

    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super().changelist_view(request, extra_context=my_context)
    # TODO : Export to excel
    # TODO : Credit feature
