from django.core.management import BaseCommand, call_command
from django.utils import timezone

from config.utils.sms import BaseSMS
from employee.models import Employee


class Command(BaseCommand):

    def handle(self, *args, **options):
        employees = Employee.objects.filter(active=True,
                                            date_of_birth__day=timezone.now().day,
                                            date_of_birth__month=timezone.now().month).all()
        for employee in employees:
            message = 'Happy Birthday {full_name}. ' \
                      'Wishing you the best on your birthday and everything good in the year ahead.\n' \
                      '"Work hard. Play hard. Eat lots of cake."'

            sms = BaseSMS()
            sms.send_sms(message.format(full_name=employee.full_name), int(f"88{employee.phone}"))
