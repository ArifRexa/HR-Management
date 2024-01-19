from django.urls import path
from account.views import payment_voucher

app_name = 'account'

urlpatterns = [
    path('payment-voucher/<int:id>/', payment_voucher, name='payment_voucher'),
]
