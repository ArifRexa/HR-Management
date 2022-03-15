from django.core.management import BaseCommand
from datetime import datetime

from project_management.models import ProjectResourceEmployee


class Command(BaseCommand):
    help = 'Closes or Deduct Employees form Project Resource When allocated hour will be expired'

    def handle(self, *args, **options):
        project_resource_employees = ProjectResourceEmployee.objects.all()
        for resource in project_resource_employees:
            if resource.end_date <= datetime.now():
                resource.delete()
