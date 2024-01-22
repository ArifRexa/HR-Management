from django.urls import path
from account.views import payment_voucher, account_journal

app_name = 'account'

urlpatterns = [
    path('payment-voucher/<int:id>/', payment_voucher, name='payment_voucher'),
    path('account-journal/<int:id>/', account_journal, name='account_journal'),
]
