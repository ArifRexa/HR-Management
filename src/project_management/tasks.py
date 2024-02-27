from datetime import datetime, timedelta

from django.core import management
from django_q.tasks import async_task
from project_management.models import ObservationProject
from employee.models.employee import Observation

def mark_employee_free():
    management.call_command('mark_employee_free')

def delete_new_proj():
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        deleted_count, _ = ObservationProject.objects.filter(created_at__lt=two_weeks_ago).delete()
        deleted_employee = Observation.objects.filter(created_at__lt=two_weeks_ago).delete()
