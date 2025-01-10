from django.urls import path, include
from . import views


urlpatterns = [
    path('<project_hash>/', views.get_weekly_project_report, name="project-update-for-client"),
]