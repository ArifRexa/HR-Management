from django.urls import path

from account.views import BalanceSummery

urlpatterns = [
    path('balance/', BalanceSummery.as_view(), name='balance')
]
