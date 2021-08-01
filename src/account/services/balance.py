from datetime import datetime, timedelta, date

from dateutil.relativedelta import relativedelta
from django.db.models import Sum

from account.models import SalarySheet, Expense, Income


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
