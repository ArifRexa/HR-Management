from academy.views import MarketingSliderAPIListView
from django.urls import path

urlpatterns = [
    path("marketing/sliders/", MarketingSliderAPIListView.as_view()),
]