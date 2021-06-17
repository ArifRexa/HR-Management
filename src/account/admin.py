from datetime import datetime
from django.contrib import admin
from django.db.models import Sum, Q

from account.models import SalarySheet, EmployeeSalary, Expense
from account.repository.SalarySheetRepository import SalarySheetRepository
from employee.models import Employee


class EmployeeSalaryInline(admin.TabularInline):
    model = EmployeeSalary
    extra = 0
    readonly_fields = ('employee', 'net_salary', 'overtime', 'project_bonus', 'leave_bonus', 'gross_salary',)
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(SalarySheet)
class SalarySheetAdmin(admin.ModelAdmin):
    list_display = ('date', 'created_at', 'total')
    fields = ('date',)
    inlines = (EmployeeSalaryInline,)

    def save_model(self, request, salary_sheet, form, change):
        salary = SalarySheetRepository()
        salary.save(request.POST['date'])

    def total(self, obj):
        return EmployeeSalary.objects.filter(salary_sheet_id=obj.id).aggregate(Sum('gross_salary'))['gross_salary__sum']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'amount', 'note', 'created_by')
    date_hierarchy = 'date'

    change_list_template = 'admin/expense/list.html'

    def get_total_hour(self, request):
        filters = {}
        for key in dict(request.GET):
            filters[key] = request.GET.get(key)

        dataset = Expense.objects.filter(*[Q(**{key: value}) for key, value in filters.items() if value])
        return dataset.aggregate(tot=Sum('amount'))['tot']

    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super().changelist_view(request, extra_context=my_context)
