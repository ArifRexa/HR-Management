from django.shortcuts import render

from django.contrib import admin, messages
from django.http import HttpResponse
from django.template import loader, Context, Template
from django.utils.text import slugify
from django_q.tasks import async_task
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

import config.settings
from config.utils.pdf import PDF
from employee.models import Employee
from settings.models import FinancialYear

from django.contrib.admin import helpers

from ._forms import NOCIntermediateForm



NOC_MAIL_DATA = """
<h3>Dear {{ employee.full_name | title }},</h3>
<p>This is to certify that {{ employee.full_name | title }}, who was working as {{ employee.designation }} at
    Mediusware Ltd
    since {{ employee.joining_date }}
    to {{ employee.resignation_date }}. He was a sincere employee of our company.
</p>
<p> This certificate is presented to claim completed No Objection upon {{ employee.full_name | title }}, if any
    organization hires him
    and he provides his services to any other firm as his employment period with our organization is over. This
    certificate is issued on the request of employee and therefore we hold no further responsibility. During his
    working span with us he proves to be sincere. We wish him good luck.
</p>
"""

NOC_PDF_DATA = """
<p>This is to certify that <b>{{ employee.full_name | title }}</b>, who was working as
    <b>{{ employee.designation }}</b> at <b>Mediusware Ltd.</b>
    since <b>{{ employee.joining_date }}</b>
    to <b>{{ employee.resignation_date }}</b>. He/She was a sincere employee of our company.
</p>
<p>This certificate is presented to claim completed No Objection upon <b>{{ employee.full_name | title }}</b>, if any
    organization hires him / her
    and he/she provides his services to any other firm as his employment period with our organization is over. This
    certificate is issued on the request of employee and therefore we hold no further responsibility. During his
    working span with us he/she proves to be sincere. We wish him/her good luck. 
</p>
"""


class EmployeeActions:
    actions = ['print_appointment_letter', 'print_permanent_letter', 'print_increment_letter', 'print_noc_letter',
               'print_resignation_letter', 'print_tax_salary_certificate', 'print_salary_certificate',
               'print_bank_forwarding_letter', 'print_promotion_letter',
               'mail_appointment_letter', 'mail_permanent_letter', 'mail_increment_letter', 'mail_noc_letter',
               'download_employee_info']

    @admin.action(description='Print Appointment Letter')
    def print_appointment_letter(self, request, queryset):
        return self.generate_pdf(request, queryset=queryset, letter_type='EAL').render_to_pdf()

    @admin.action(description='Print Permanent Letter')
    def print_permanent_letter(self, request, queryset):
        return self.generate_pdf(request, queryset=queryset, letter_type='EPL').render_to_pdf()

    @admin.action(description='Print Increment Letter')
    def print_increment_letter(self, request, queryset):
        return self.generate_pdf(request, queryset=queryset, letter_type='EIL').render_to_pdf()

    @admin.action(description='Print Promotion Letter')
    def print_promotion_letter(self, request, queryset):
        return self.generate_pdf(request, queryset=queryset, letter_type='EPRL').render_to_pdf()

    @admin.action(description='Print NOC Letter')
    def print_noc_letter(self, request, queryset):
        employee = queryset.first()
        
        if "noc_intermediate" in request.POST:
            form = NOCIntermediateForm(data=request.POST)
            if form.is_valid():
                return self.generate_pdf(
                    request, 
                    queryset=(employee, ), 
                    letter_type='NOC', 
                    extra_context={
                        'noc_body': form.cleaned_data.get('noc_body', ''),
                    },
                ).render_to_pdf()
        
        from django.template import Context, Template
        t = Template(NOC_PDF_DATA)
        c = Context({'employee': employee})
        html = t.render(c)
        
        form = NOCIntermediateForm(noc_body=html)
        return render(
            request,
            "admin/employee/noc_intermediate.html", 
            context={
                **self.admin_site.each_context(request),
                'action_name': 'print_noc_letter',
                'queryset': queryset,
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
                'form': form,
            }
        )

    def print_resignation_letter(self, request, queryset):
        return self.generate_pdf(request, queryset=queryset, letter_type='ERL').render_to_pdf()

    @admin.action(description='Print Salary Certificate (For Yearly Tax Return)')
    def print_tax_salary_certificate(self, request, queryset):
        context = {'financial_year': FinancialYear.objects.filter(active=True).first()}
        return self.generate_pdf(request, queryset=queryset, letter_type='ESC', context=context).render_to_pdf()

    @admin.action(description='Print Salary Certificate (Last month)')
    def print_salary_certificate(self, request, queryset):
        return self.generate_pdf(request, queryset=queryset, letter_type='ELMSC').render_to_pdf()

    @admin.action(description="Print Salary Account Forwarding Letter")
    def print_bank_forwarding_letter(self, request, queryset):
        return self.generate_pdf(request, queryset=queryset, letter_type='AFL').render_to_pdf()

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
        employee = queryset.first()
        
        if "noc_intermediate" in request.POST:
            form = NOCIntermediateForm(data=request.POST)
            if form.is_valid():
                self.__send_mail(
                    (employee, ),
                    letter_type='NOC', 
                    subject='No Objection Certificate (NOC)',
                    mail_template='mails/noc.html',
                    extra_context={
                        'noc_body': form.cleaned_data.get('noc_body', ''),
                    },
                    request=request,
                )
                return
        
        t = Template(NOC_MAIL_DATA)
        c = Context({'employee': employee})
        html = t.render(c)
        
        form = NOCIntermediateForm(noc_body=html)
        return render(
            request,
            "admin/employee/noc_intermediate.html", 
            context={
                **self.admin_site.each_context(request),
                'action_name': 'mail_noc_letter',
                'queryset': queryset,
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
                'form': form,
            }
        )

    @admin.action()
    def mail_salary_certificate(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type='ESC', subject='No objection certificate (NOC)',
            mail_template='mails/noc.html',
            request=request
        )

    @admin.action(description='Download all active employee information')
    def download_employee_info(self, request, queryset):
        wb = Workbook()
        work_sheets = {}
        work_sheet = wb.create_sheet(title='Employee List')
        work_sheet.append(
            ['Name', 'Designation', 'Phone', 'Email', 'Address']
        )
        for employee in Employee.objects.filter(active=True).all():
            work_sheet.append(
                [employee.full_name, employee.designation.title, employee.phone, employee.email, employee.address]
            )
        work_sheets['employee'] = work_sheet
        wb.remove(wb['Sheet'])
        response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=Employees.xlsx'
        return response

    def __send_mail(self, queryset, letter_type, subject, mail_template, request, extra_context:dict={}):
        for employee in queryset:
            pdf = self.generate_pdf(request, queryset=(employee,), letter_type=letter_type, extra_context=extra_context).create()
            context = {
                'employee': employee,
                **extra_context,
            }
            context.update(extra_context)
            html_body = loader.render_to_string(mail_template, context=context)
            async_task('employee.tasks.send_mail_to_employee', employee, pdf, html_body, subject)
        self.message_user(request, 'Mail sent successfully', messages.SUCCESS)

    # Download generated pdf ile
    def generate_pdf(self, request, queryset, letter_type='EAL', context=None, extra_context={}):
        pdf = PDF()
        pdf.file_name = f'{self.create_file_name(queryset)}{letter_type}'
        pdf.template_path = self.get_letter_type(letter_type)
        pdf.context = {
            'employees': queryset,
            **extra_context,
            'latter_type': letter_type,
            'context': context,
            'seal': f"{config.settings.STATIC_ROOT}/stationary/sign_md.png"
        }
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
