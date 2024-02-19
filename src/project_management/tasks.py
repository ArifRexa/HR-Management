from datetime import datetime, timedelta

from django.core import management
from project_management.models import ObservationProject
from employee.models.employee import Observation

def mark_employee_free():
    management.call_command('mark_employee_free')

def delete_new_proj(self, *args, **kwargs):
        # Calculate the date two weeks ago
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        
        # Filter and delete data older than two weeks
        deleted_count, _ = ObservationProject.objects.filter(created_at__lt=two_weeks_ago).delete()
        deleted_employee = Observation.objects.filter(created_at__lt=two_weeks_ago).delete()
        # Output result
        self.stdout.write(self.style.SUCCESS(f'{deleted_count} {deleted_employee} records deleted successfully'))