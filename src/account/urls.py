from django.urls import path
from account.views import payment_voucher, account_journal, costs_by_expense_group, balance_sheet

app_name = 'account'

urlpatterns = [
    path('payment-voucher/<int:id>/', payment_voucher, name='payment_voucher'),
    path('account-journal/<int:id>/', account_journal, name='account_journal'),
    path('group-expenses-costs/<int:id>/', costs_by_expense_group, name='group_costs'),
    path('balance_sheet/<int:id>/', balance_sheet, name='balance_sheet'),
]
