from django.urls import path, include
from . import views


urlpatterns = [
    path(
        "<project_hash>/",
        views.get_weekly_project_report,
        name="project-update-for-client",
    ),
    # path('<project_hash>/', views.get_project_updates, name="project-update-for-client"),
    path(
        "client/meeting/create/form/",
        views.get_client_meeting_form,
        name="meeting_form",
    ),
    path(
        "client/meeting/create/",
        views.create_client_meeting,
        name="meeting_create",
    ),
    path("update-client-meeting-form/<int:pk>/", views.update_client_meeting_form, name="update_meeting_form")
]
