from django.core.management import BaseCommand

from employee.models import Employee
from employee.models.employee_activity import EmployeeProject


class Command(BaseCommand):
    def handle(self, *args, **options):
        employees = Employee.objects.filter(active=True).all()
        for employee in employees:
            obj, created = EmployeeProject.objects.update_or_create(
                employee=employee
            )
