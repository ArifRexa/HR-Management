from django.urls import include, path
from rest_framework import routers

from .views import (
    DailyProjectUpdateViewSet,
    ProjectViewSet,
    TeamViewSet,
    WeeklyProjectHoursViewSet,
    WeeklyProjectUpdateViewSet,
    ProjectResourceListView,
)

router = routers.DefaultRouter()

router.register("daily-project-update", DailyProjectUpdateViewSet)
router.register("project-update", WeeklyProjectUpdateViewSet, basename="project-update")
router.register("resources", ProjectResourceListView, basename="project-resources")
router.register("projects", ProjectViewSet, basename="projects")
router.register(r"teams", TeamViewSet, basename='teams')
router.register(r'weekly-project-hours', WeeklyProjectHoursViewSet, basename='weekly-project-hours')


urlpatterns = [
    path("", include(router.urls)),
]
