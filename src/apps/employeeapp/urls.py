from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    EmployeeDashboardView,
    EmployeeViewSet,
    EmployeeProjectHourStatisticView,
    NearByEmployeesBirthDayView,
    BookConferenceRoomListCreateView,
)


router = DefaultRouter()

router.register("", EmployeeViewSet)

urlpatterns = [
    *router.urls,
    path("dashboard", EmployeeDashboardView.as_view(), name="dashboard"),
    path("project-hour-statistic", EmployeeProjectHourStatisticView.as_view(), name="project-hour-statistic"),
    path("near-by-employees-birthday", NearByEmployeesBirthDayView.as_view(), name="employees-birthday"),
    path("book-conference-rooms", BookConferenceRoomListCreateView.as_view(), name="book-conference-room"),
]