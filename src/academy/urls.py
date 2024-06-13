from academy.views import MarketingSliderAPIListView, TrainingListAPIView, TrainingRetrieveAPIView
from django.urls import path

urlpatterns = [
    path("marketing/sliders/", MarketingSliderAPIListView.as_view(), name="marketing_slider"),
    path("training/<int:pk>/", TrainingRetrieveAPIView.as_view(), name="training"),
    path("trainings/", TrainingListAPIView.as_view(), name="trainings"),
]