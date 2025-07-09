from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    CredentialCategoryViewSet,
    CredentialViewSetView,
    EmployeeAttendanceListView,
    EmployeeDashboardView,
    EmployeeViewSet,
    EmployeeProjectHourStatisticView,
    NearByEmployeesBirthDayView,
    BookConferenceRoomListCreateView,
    EmployeeLateAttendanceFine,
    EmployeeLeaveView,
)


router = DefaultRouter()

router.register("credentials", CredentialViewSetView, basename="employee-credentials")
router.register("credential-categories", CredentialCategoryViewSet, basename="credential-category")
router.register("leaves", EmployeeLeaveView, basename="employee-leave")
router.register("", EmployeeViewSet)

urlpatterns = [
    *router.urls,
    path("attendance", EmployeeAttendanceListView.as_view(), name="employee-attendance"),
    path("late-attendance-fine", EmployeeLateAttendanceFine.as_view(), name="late-fine"),
    path("dashboard", EmployeeDashboardView.as_view(), name="dashboard"),
    path("project-hour-statistic", EmployeeProjectHourStatisticView.as_view(), name="project-hour-statistic"),
    path("near-by-employees-birthday", NearByEmployeesBirthDayView.as_view(), name="employees-birthday"),
    path("book-conference-rooms", BookConferenceRoomListCreateView.as_view(), name="book-conference-room"),
]
