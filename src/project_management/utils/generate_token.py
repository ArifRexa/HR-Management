from uuid import uuid4
from project_management.models import Project, ProjectToken


def generate_token():
    projects = Project.objects.filter(active=True)
    for project in projects:
        ProjectToken.objects.update_or_create(
            project_id=project.id,
            defaults={
                'token': uuid4()
            }
        )
    # Safety
    ProjectToken.objects.filter(project__active=False).delete()


def generate_identifier():
    projects = Project.objects.all()
    for project in projects:
        if project.identifier is None:
            project.identifier = uuid4()
            project.save()
