from time import sleep

from django.contrib import admin
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mass_mail, send_mail
from django.http import QueryDict
from django.template import loader
from django.template.loader import get_template
from django.utils.text import slugify
from django_q.tasks import async_task

from config.utils.pdf import PDF
from employee.tasks import send_mail_to_employee


class EmployeeActions:
    actions = ['print_appointment_letter', 'print_permanent_letter', 'print_increment_letter',
               'mail_appointment_letter']

    @admin.action(description='Print Appointment Letter')
    def print_appointment_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='EAL').render_to_pdf()

    @admin.action(description='Print Permanent Letter')
    def print_permanent_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='EPL').render_to_pdf()

    @admin.action(description='Print Increment Letter')
    def print_increment_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='EIL').render_to_pdf()

    @admin.action(description='Mail Appointment Letter')
    def mail_appointment_letter(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type='EAL', subject='Appointment letter',
            mail_template='mails/appointment.html'
        )

    def __send_mail(self, queryset, letter_type, subject, mail_template):
        for employee in queryset:
            pdf = self.generate_pdf(queryset=(employee,), letter_type=letter_type).create()
            html_body = loader.render_to_string(mail_template, context={'employee': employee})
            print(html_body)
            async_task('employee.tasks.send_mail_to_employee', employee, pdf, html_body, subject)

    # Download generated pdf ile
    def generate_pdf(self, queryset, letter_type='EAL'):
        pdf = PDF()
        pdf.file_name = f'{self.create_file_name(queryset)}{letter_type}'
        pdf.template_path = self.get_letter_type(letter_type)
        pdf.context = {'employees': queryset, 'latter_type': letter_type}
        return pdf

    # generate file using selected employees
    def create_file_name(self, queryset):
        file_name = ''
        for value in queryset:
            file_name += f'{slugify(value.full_name)}-'
        return file_name

    def get_letter_type(self, letter_type):
        switcher = {
            'EAL': 'letters/appointment_latter.html',
            'EPL': 'letters/permanent_letter.html',
            'EIL': 'letters/increment_latter.html',
        }
        return switcher.get(letter_type, '')
