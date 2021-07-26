import datetime
from datetime import timedelta, date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.db.models import Sum, Model
from django.utils import timezone
from django.views.generic import TemplateView, ListView

from account.models import Expense, SalarySheet, Income, EmployeeSalary


class AdminOnly(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class BalanceSummery(AdminOnly, TemplateView):
    template_name = 'admin/balance/balance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=356)
        result = []
        while start_date < end_date + relativedelta(months=1):
            result.append(self._get_pl(start_date))
            start_date += relativedelta(months=1)
        context['month_list'] = result[::-1]
        context['site_title'] = 'Mediusware Ltd'
        context['is_nav_sidebar_enabled'] = True
        context['has_permission'] = True
        context['start_date'] = start_date
        context['end_date'] = end_date
        return context

    def _get_pl(self, date: date):
        filter = {
            'date__month': date.month,
            'date__year': date.year
        }
        salary = SalarySheet.objects.filter(**filter).first()
        salary = salary.total if salary else 0
        expense = self.__sum_total(Expense.objects.filter(**filter).all(), 'amount')
        income = self.__sum_total(Income.objects.filter(**filter).filter(status='approved').all(), 'payment')
        return {
            'expense': expense,
            'salary': salary,
            'income': income,
            'date': date,
            'pl': income - (expense + salary)
        }

    def __sum_total(self, queryset, column):
        total = queryset.aggregate(total=Sum(column))['total']
        if total is None:
            return 0
        return total
