from django.urls import path, include
from . import views


urlpatterns = [
    path('<project_hash>/', views.get_project_updates, name="project-update-for-client"),
]