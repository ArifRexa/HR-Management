from django.urls import include, path
from rest_framework import routers

from .views import (
    DailyProjectUpdateViewSet,
    ProjectViewSet,
    WeeklyProjectUpdateViewSet,
    ProjectResourceListView,
)

router = routers.DefaultRouter()

router.register("daily-project-update", DailyProjectUpdateViewSet)
router.register("project-update", WeeklyProjectUpdateViewSet, basename="project-update")
router.register("resources", ProjectResourceListView, basename="project-resources")
router.register("projects", ProjectViewSet, basename="projects")

urlpatterns = [
    path("", include(router.urls)),
]
