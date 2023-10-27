from django.shortcuts import render

from project_management.models import Project, DailyProjectUpdate


# Create your views here.
def get_project_updates(request, project_hash):
    print(project_hash)
    project_obj = Project.objects.get(identifier=project_hash)
    daily_updates = DailyProjectUpdate.objects.filter(project=project_obj)

    out_dict = {
        'project':project_obj,
        'daily_updates':daily_updates
    }

    return render(request, 'client_management/project_details.html', out_dict)