# # src/news_letter/urls.py

# from django.urls import path
# from news_letter.views import SubscriberAPIView

# urlpatterns = [
#     path('website/subscribers/', SubscriberAPIView.as_view(), name='subscriber-api'),
#     path('website/subscribers/<int:identifier>/', SubscriberAPIView.as_view(), name='subscriber-api-detail'),
# ]


# src/news_letter/urls.py

from django.urls import path
from news_letter.views import SubscriberListView, SubscriberDetailView

urlpatterns = [
    path('website/subscribers/', SubscriberListView.as_view(), name='subscriber-list'),
    path('website/subscribers/<int:identifier>/', SubscriberDetailView.as_view(), name='subscriber-detail'),
]