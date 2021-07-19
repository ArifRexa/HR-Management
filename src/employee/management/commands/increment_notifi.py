import datetime

from django.core.management import BaseCommand

from employee.models import SalaryHistory, Employee
from employee.tasks import increment_notification


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(datetime.datetime.now() - datetime.timedelta(days=160))
        employees = Employee.objects.filter(
            salaryhistory__active_from__exact=datetime.datetime.now() - datetime.timedelta(days=160)
        ).all()
        for employee in employees:
            print(f"{employee.full_name} has incremented at {employee.current_salary.active_from}")
        if len(employees) > 0:
            increment_notification(employees)
