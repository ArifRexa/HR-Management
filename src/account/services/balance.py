from datetime import datetime, timedelta, date

from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from account.models import SalarySheet, Expense, Income, ProfitShare


class BalanceSummery:

    def get_context_data(self):
        context = {}
        end_date = date.today()
        start_date = end_date - timedelta(days=356)
        result = []
        while start_date < end_date + relativedelta(months=1):
            result.append(self._get_pl(start_date))
            start_date += relativedelta(months=1)
        context['month_list'] = result[::-1]
        context['start_date'] = start_date
        context['end_date'] = end_date
        print(result)
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
        profit_share_with_rifat = ((income - (expense + salary)) * 25) / 100
        payment_done = ProfitShare.objects.filter(**filter).filter(user_id=1).aggregate(
            monthly_payment_amount=Coalesce(Sum('payment_amount'), Value(0.0))
        )['monthly_payment_amount']

        return {
            'expense': expense,
            'salary': salary,
            'income': income,
            'date': date,
            'pl': income - (expense + salary),
            'rifat': profit_share_with_rifat,
            'payment': payment_done,
            'due': profit_share_with_rifat - payment_done
        }

    def __sum_total(self, queryset, column):
        total = queryset.aggregate(total=Sum(column))['total']
        if total is None:
            return 0
        return total
