from time import sleep

from django.contrib import admin
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import QueryDict
from django.template import loader
from django.template.loader import get_template
from django.utils.text import slugify

from config.utils.pdf import PDF


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
        for employee in queryset:
            pdf = self.generate_pdf(queryset=(employee,), letter_type='EAL')
            html_mail = loader.render_to_string('mails/appointment.html')
            email = EmailMultiAlternatives()
            email.subject = 'DD'
            email.attach_alternative(html_mail, 'text/html')
            email.to = ['kmrifat@gmail.com']
            email.attach_file(pdf.create())
            email.send()
            pdf.delete()

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
