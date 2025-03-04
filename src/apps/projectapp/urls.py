from django.urls import path
from rest_framework import routers

from .views import (
    DailyProjectUpdateViewSet,
    WeeklyProjectUpdateViewSet,
)
from django.urls import include


router = routers.DefaultRouter()

router.register("daily-project-update", DailyProjectUpdateViewSet)
router.register("project-update", WeeklyProjectUpdateViewSet, basename="project-update")
urlpatterns = [path("", include(router.urls))]