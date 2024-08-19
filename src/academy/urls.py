from academy.views import (
    FAQListView,
    HomePageAPIView,
    InstructorFeedbackView,
    MarketingSliderAPIListView,
    StudentCreateAPIView,
    SuccessStoryView,
    TrainingListAPIView,
    TrainingRetrieveAPIView,
    OurAchievementListView
)
from django.urls import path

urlpatterns = [
    path(
        "marketing/sliders/",
        MarketingSliderAPIListView.as_view(),
        name="marketing_slider",
    ),
    path(
        "our-achievement/",
        OurAchievementListView.as_view(),
        name="our_achievement",
    ),
    path("training/<slug:slug>/", TrainingRetrieveAPIView.as_view(), name="training"),
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
    path("faq/", FAQListView.as_view(), name="faq"),
]
