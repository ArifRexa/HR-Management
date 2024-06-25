from academy.views import (
    HomePageAPIView,
    InstructorFeedbackView,
    MarketingSliderAPIListView,
    StudentCreateAPIView,
    SuccessStoryView,
    TrainingListAPIView,
    TrainingRetrieveAPIView,
)
from django.urls import path

urlpatterns = [
    path(
        "marketing/sliders/",
        MarketingSliderAPIListView.as_view(),
        name="marketing_slider",
    ),
    path("training/<int:pk>/", TrainingRetrieveAPIView.as_view(), name="training"),
    path("trainings/", TrainingListAPIView.as_view(), name="trainings"),
    path("student/", StudentCreateAPIView.as_view(), name="student"),
    path("success/story", SuccessStoryView.as_view(), name="success_story"),
    path(
        "instructor-feedback/",
        InstructorFeedbackView.as_view(),
        name="instructor_feedback",
    ),
    path(
        "home/why-we-best/",
        HomePageAPIView.as_view(),
        name="why_we_best",
    ),
]
