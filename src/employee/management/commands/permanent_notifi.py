import datetime
from datetime import timedelta

from django.core.management import BaseCommand

from employee.models import Employee


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(datetime.datetime.now() - timedelta(days=100))
        employees = Employee.objects.filter(
            joining_date__exact=datetime.datetime.now() - timedelta(days=80),
            permanent_date__isnull=True
        ).all()
        for employee in employees:
            print(f"{employee.full_name} has joined at {employee.joining_date}")
