import datetime

from django.core.management import BaseCommand

from account.models import EmployeeSalary


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(datetime.datetime.now() - datetime.timedelta(days=100))
        employees = EmployeeSalary.objects.filter(
            joining_date__exact=datetime.datetime.now() - datetime.timedelta(days=80),
            permanent_date__isnull=True
        ).all()
        for employee in employees:
            print(f"{employee.full_name} has joined at {employee.joining_date}")
