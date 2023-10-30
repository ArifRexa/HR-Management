from django.apps import AppConfig


class ClientManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'client_management'

    def ready(self):
        from project_management.models import Project, create_project_identifier

        for project in Project.objects.all():
            project.identifier = create_project_identifier()
            project.save()