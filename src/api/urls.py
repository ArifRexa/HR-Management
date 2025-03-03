from django.urls import path
from rest_framework import routers

from api.views import DailyProjectUpdateViewSet, EmployeeViewSet, UserViewSet
from django.urls import include


router = routers.DefaultRouter()

router.register("daily-project-update", DailyProjectUpdateViewSet)
router.register("users", UserViewSet)
router.register("employees", EmployeeViewSet)
urlpatterns = [path("", include(router.urls))]
