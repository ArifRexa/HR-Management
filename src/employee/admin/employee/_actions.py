from django.contrib import admin, messages
from django.db.models import Sum
from django.template import loader
from django.utils.text import slugify
from django_q.tasks import async_task

import config.settings
from config.utils.pdf import PDF
from employee.models import Employee
from settings.models import FinancialYear


class EmployeeActions:
    actions = ['print_appointment_letter', 'print_permanent_letter', 'print_increment_letter', 'print_noc_letter',
               'print_resignation_letter', 'print_tax_salary_certificate', 'print_salary_certificate',
               'print_bank_forwarding_letter', 'print_promotion_letter',
               'mail_appointment_letter', 'mail_permanent_letter', 'mail_increment_letter', 'mail_noc_letter']

    @admin.action(description='Print Appointment Letter')
    def print_appointment_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='EAL').render_to_pdf()

    @admin.action(description='Print Permanent Letter')
    def print_permanent_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='EPL').render_to_pdf()

    @admin.action(description='Print Increment Letter')
    def print_increment_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='EIL').render_to_pdf()

    @admin.action(description='Print Promotion Letter')
    def print_promotion_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='EPRL').render_to_pdf()

    @admin.action(description='Print NOC Letter')
    def print_noc_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='NOC').render_to_pdf()

    def print_resignation_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='ERL').render_to_pdf()

    @admin.action(description='Print Salary Certificate (For Yearly Tax Return)')
    def print_tax_salary_certificate(self, request, queryset):
        context = {'financial_year': FinancialYear.objects.filter(active=True).first()}
        return self.generate_pdf(queryset=queryset, letter_type='ESC', context=context).render_to_pdf()

    @admin.action(description='Print Salary Certificate (Last month)')
    def print_salary_certificate(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='ELMSC').render_to_pdf()

    @admin.action(description="Print Salary Account Forwarding Letter")
    def print_bank_forwarding_letter(self, request, queryset):
        return self.generate_pdf(queryset=queryset, letter_type='AFL').render_to_pdf()

    @admin.action(description='Mail Appointment Letter')
    def mail_appointment_letter(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type='EAL', subject='Appointment letter',
            mail_template='mails/appointment.html',
            request=request
        )

    @admin.action()
    def mail_permanent_letter(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type='EPL', subject='Permanent letter',
            mail_template='mails/permanent.html',
            request=request
        )

    @admin.action
    def mail_increment_letter(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type='EIL', subject='Increment letter',
            mail_template='mails/increment.html',
            request=request
        )

    @admin.action(description="Mail NOC letter")
    def mail_noc_letter(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type='NOC', subject='No objection certificate (NOC)',
            mail_template='mails/noc.html',
            request=request
        )

    @admin.action()
    def mail_salary_certificate(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type='ESC', subject='No objection certificate (NOC)',
            mail_template='mails/noc.html',
            request=request
        )

    def __send_mail(self, queryset, letter_type, subject, mail_template, request):
        for employee in queryset:
            pdf = self.generate_pdf(queryset=(employee,), letter_type=letter_type).create()
            html_body = loader.render_to_string(mail_template, context={'employee': employee})
            async_task('employee.tasks.send_mail_to_employee', employee, pdf, html_body, subject)
        self.message_user(request, 'Mail sent successfully', messages.SUCCESS)

    # Download generated pdf ile
    def generate_pdf(self, queryset, letter_type='EAL', context=None):
        pdf = PDF()
        pdf.file_name = f'{self.create_file_name(queryset)}{letter_type}'
        pdf.template_path = self.get_letter_type(letter_type)
        pdf.context = {'employees': queryset, 'latter_type': letter_type,
                       'context': context,
                       'seal': f"{config.settings.STATIC_ROOT}/stationary/sign_md.png"}
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
            'NOC': 'letters/noc_letter.html',
            'ERL': 'letters/resignation_letter.html',
            'ESC': 'letters/salary_certificate.html',
            'ELMSC': 'letters/salary_certificate_last_month.html',
            'AFL': 'letters/salary_account_forwarding_letter.html',
            'EPRL': 'letters/promotion_letter.html'
        }
        return switcher.get(letter_type, '')
