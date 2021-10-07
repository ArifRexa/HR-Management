import time

from django.core.management import BaseCommand
from django.db.models import QuerySet
from django_q.tasks import async_task

from config.utils.sms import BaseSMS
from employee.models import Employee


class Command(BaseCommand):
    argument = 'employees'
    msg = 'message'

    def add_arguments(self, parser):
        parser.add_argument(f'{self.argument}', nargs="+", type=int)
        parser.add_argument(f'{self.msg}', type=str)

    def handle(self, *args, **options):
        employees = Employee.objects.filter(pk__in=options[f'{self.argument}'])
        for employee in employees:
            async_task('employee.management.commands.sms_notification_to_employee.send_sms',
                       employee,
                       options[f'{self.msg}'],
                       group=f'{employee.full_name} Got SMS Announce')


def send_sms(employee: Employee, message):
    formatted_message = message.format(full_name=employee.full_name, email=employee.email, phone=employee.phone,
                                       address=employee.address)
    sms = BaseSMS()
    sms.send_sms(formatted_message, contact_number=int(f'88{employee.phone}'))
