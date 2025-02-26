from django.urls import path
from rest_framework import routers

from api.views import DailyProjectUpdateViewSet
from django.urls import include


router = routers.DefaultRouter()

router.register("project-update", DailyProjectUpdateViewSet)

urlpatterns = [path("", include(router.urls))]
