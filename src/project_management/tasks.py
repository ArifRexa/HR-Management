from django.core import management


def mark_employee_free():
    management.call_command('mark_employee_free')
