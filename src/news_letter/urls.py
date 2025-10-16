# src/news_letter/urls.py
from django.urls import path
from news_letter.views import CaseStudySubscriptionView, SubscriberListView, SubscriberDetailView

urlpatterns = [
    path('website/subscribers/', SubscriberListView.as_view(), name='subscriber-list'),
    path('website/subscribers/<int:identifier>/', SubscriberDetailView.as_view(), name='subscriber-detail'),

    path('api/case-study-subscribe/', CaseStudySubscriptionView.as_view(), name='case-study-subscribe'),
]
