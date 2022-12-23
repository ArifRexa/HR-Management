from uuid import uuid4
from project_management.models import Project, ProjectToken


def generate_token():
    projects = Project.objects.filter(active=True)
    for project in projects:
        ProjectToken.objects.update_or_create(
            project_id=project.id,
            defaults= {
                'token': uuid4()
            }
        )
    # Safety
    ProjectToken.objects.filter(project__active=False).delete()
