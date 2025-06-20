from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    EmployeeDashboardView,
    EmployeeViewSet,
    EmployeeProjectHourStatisticView,
)


router = DefaultRouter()

router.register("", EmployeeViewSet)

urlpatterns = [
    *router.urls,
    path("dashboard", EmployeeDashboardView.as_view(), name="dashboard"),
    path("project-hour-statistic", EmployeeProjectHourStatisticView.as_view(), name="project-hour-statistic"),
]