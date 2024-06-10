import datetime

from django.core.management import BaseCommand
from django.db.models import Q, F, Exists

from employee.models import SalaryHistory, Employee
from employee.tasks import increment_notification


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_to_check = datetime.datetime.now() - datetime.timedelta(days=160)
        
        employees = Employee.objects.filter(
            salaryhistory__active_from__exact=data_to_check,
            active=True
        ).all()
        incrementable_employees = []
        for employee in employees:
            if employee.current_salary.active_from == data_to_check.date():
                incrementable_employees.append(employee)
                print(f"{employee.full_name} has incremented at {employee.current_salary.active_from}")
        if len(incrementable_employees) > 0:
            increment_notification(incrementable_employees)
