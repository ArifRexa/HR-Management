from rest_framework.routers import DefaultRouter

from .views import EmployeeDashboardView, EmployeeViewSet
from django.urls import path


router = DefaultRouter()

router.register("", EmployeeViewSet)

urlpatterns = [
    *router.urls,
    path("dashboard", EmployeeDashboardView.as_view(), name="dashboard"),
]