import datetime
from datetime import date

from dateutil.utils import today
from django.contrib import admin
from django.contrib.admin import AdminSite, RelatedOnlyFieldListFilter
from django.contrib.auth.models import User
from django.db.models import Sum, Q, Value, QuerySet, Func, F, CharField
from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import format_html

from account.models import Expense, ExpenseCategory, ExpanseAttachment, ExpenseGroup
from config.admin.utils import simple_request_filter
from config.utils.pdf import PDF
from employee.models import Employee

from django.contrib import messages


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')
    search_fields = ['title']

    def has_module_permission(self, request):
        return False


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')
    search_fields = ['title']

    def has_module_permission(self, request):
        return False


class ExpanseAttachmentInline(admin.TabularInline):
    model = ExpanseAttachment
    extra = 1


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'expanse_group', 'expense_category', 'get_amount', 'note', 'created_by', 'is_approved')
    date_hierarchy = 'date'
    list_filter = ['is_approved', ('created_by', RelatedOnlyFieldListFilter,),'expanse_group', 'expense_category', 'date']
    change_list_template = 'admin/expense/list.html'
    inlines = [ExpanseAttachmentInline]
    search_fields = ['note']
    actions = ('print_voucher', 'approve_expense',)
    autocomplete_fields = ('expanse_group', 'expense_category')

    def get_readonly_fields(self, request, obj):
        rfs = super().get_readonly_fields(request, obj)
        rfs += ('approved_by', )
        if not request.user.is_superuser and not request.user.has_perm("account.can_approve_expense"):
            rfs += ('is_approved', )
        return rfs
    
    def has_change_permission(self, request, obj=None):
        perm = super().has_change_permission(request, obj)
        if perm and obj:
            if not request.user.is_superuser and not request.user.has_perm("account.can_approve_expense") and obj.is_approved:
                perm = False
        return perm
    
    @admin.display(description="Amount", ordering='amount')
    def get_amount(self, obj):
        html_template = get_template('admin/expense/list/col_amount.html')
        html_content = html_template.render({
            'expense': obj,
        })
        return format_html(html_content)
    
    def get_queryset(self, request):
        qs = super(ExpenseAdmin, self).get_queryset(request)
        if not request.user.has_perm("account.can_approve_expense") and not request.user.has_perm('account.can_view_all_expenses'):
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
    @admin.action()
    def print_voucher(self, request, queryset):
        pdf = PDF()
        pdf.context = dict(
            expense_groups=self._get_mapped_expense_data(queryset=queryset)
        )
        pdf.template_path = 'voucher/expense_voucher.html'
        return pdf.render_to_pdf(download=False)
    
    @admin.action()
    def approve_expense(self, request, queryset):
        if request.user.is_superuser or request.user.has_perm("account.can_approve_expense"):
            queryset.update(is_approved=True, approved_by=request.user)

            messages.success(request, 'Updated Successfully')
        else:
            messages.error(request, "You don't have enough permission")
        

    def _get_mapped_expense_data(self, queryset):
        mapped_date = []
        for expense in queryset.values('date', 'created_by'):
            context = dict(
                created_at=expense['date'],
                created_by=User.objects.get(id=expense['created_by']),
                data=queryset.filter(date=expense['date'], created_by=expense['created_by'])
            )
            mapped_date.append(context)
        return mapped_date
    
    def get_form(self, request, obj, **kwargs):
        if not request.user.has_perm('account.can_approve_expense'):
            self.exclude = ['is_approved']
        return super(ExpenseAdmin, self).get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change) -> None:
        if obj.is_approved == True: 
            obj.approved_by = request.user
        else:
            obj.approved_by = None
        return super().save_model(request, obj, form, change)
