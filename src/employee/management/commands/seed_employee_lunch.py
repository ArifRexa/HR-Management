from django.core.management import BaseCommand

from employee.models import Employee
from employee.models.employee import EmployeeLunch


class Command(BaseCommand):
    def handle(self, *args, **options):
        employees = Employee.objects.filter(active=True).all()
        for employee in employees:
            obj, created = EmployeeLunch.objects.update_or_create(
                employee=employee, active=True,
                defaults={'employee_id': employee.id}
            )
