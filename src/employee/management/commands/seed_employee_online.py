from django.core.management import BaseCommand

from employee.models import Employee, EmployeeOnline


class Command(BaseCommand):
    def handle(self, *args, **options):
        employees = Employee.objects.filter(active=True).all()
        for employee in employees:
            obj, created = EmployeeOnline.objects.update_or_create(
                employee=employee,
                defaults={'employee_id': employee.id}
            )
