from rest_framework.routers import DefaultRouter

from .views import DashboardView, EmployeeViewSet
from django.urls import path


router = DefaultRouter()

router.register("", EmployeeViewSet)

urlpatterns = [
    *router.urls,
    path("dashboard", DashboardView.as_view(), name="dashboard"),
]