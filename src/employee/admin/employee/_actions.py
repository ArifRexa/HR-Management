import os
from io import BytesIO

from employee.tasks import email_send_to_employee
import pdf2image
import qrcode
import requests
from django.contrib import admin, messages
from django.core.files import File
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.template import loader
from django.utils.text import slugify
from django_q.tasks import async_task
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

import config.settings
from config.utils.pdf import PDF
from employee.models import Employee, EmployeeNOC, HRPolicy
from settings.models import FinancialYear

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
    actions = [
        "generate_noc_letter",
        "print_appointment_letter",
        "print_permanent_letter",
        "print_increment_letter",
        "print_noc_letter",
        "print_resignation_letter",
        "print_tax_salary_certificate",
        "print_salary_certificate",
        "print_salary_certificate_all_months",
        "print_bank_forwarding_letter",
        "print_promotion_letter",
        "mail_role_change_letter",
        "mail_promotion_letter",
        "print_experience_letter",
        "mail_appointment_letter",
        "mail_permanent_letter",
        "mail_increment_letter",
        "mail_noc_letter",
        "download_employee_info",
        "print_salary_pay_slip_all_months",
    ]

    @admin.action(description="Print Salary Pay Slip (All months)")
    def print_salary_pay_slip_all_months(self, request, queryset):
        return self.generate_pdf(
            request, queryset=queryset, letter_type="ESPS"
        ).render_to_pdf()

    @admin.action(description="Generate NOC Letter")
    def generate_noc_letter(self, request, queryset):
        names: list[str] = []
        for obj in queryset:
            html_body = loader.render_to_string(
                "letters/noc_letter_template.html", context={"employee": obj}
            )
            enoc, enoc_created = EmployeeNOC.objects.update_or_create(
                employee_id=obj.id,
                defaults={
                    "noc_body": html_body,
                },
            )
            if not enoc.noc_pdf:
                enoc.noc_body = html_body
                names.append(obj.full_name)
        messages.success(request, f"Successfully Generated NOC for {', '.join(names)}.")

    @admin.action(description="Print Appointment Letter")
    def print_appointment_letter(self, request, queryset):
        hr_policy = (
            HRPolicy.objects.filter(active=True)
            .order_by("-created_at")
            .prefetch_related("hrpolicysection_set")
            .first()
        )
        if not hr_policy:
            hr_policies = []
        else:
            hr_policies = hr_policy.hrpolicysection_set.all()
        return self.generate_pdf(
            request=request,
            queryset=queryset,
            letter_type="EAL",
            extra_context={"hr_policies": hr_policies},
        ).render_to_pdf()

    @admin.action(description="Print Permanent Letter")
    def print_permanent_letter(self, request, queryset):
        return self.generate_pdf(
            request, queryset=queryset, letter_type="EPL"
        ).render_to_pdf()

    @admin.action(description="Print Increment Letter")
    def print_increment_letter(self, request, queryset):
        return self.generate_pdf(
            request, queryset=queryset, letter_type="EIL"
        ).render_to_pdf()

    @admin.action(description="Print Promotion Letter")
    def print_promotion_letter(self, request, queryset):
        return self.generate_pdf(
            request, queryset=queryset, letter_type="EPRL"
        ).render_to_pdf()

    @admin.action(description="Print NOC Letter")
    def print_noc_letter(self, request, queryset):
        return self.generate_pdf(
            queryset=queryset,
            letter_type="NOC",
            request=request,
        ).render_to_pdf()

    def print_resignation_letter(self, request, queryset):
        return self.generate_pdf(
            request, queryset=queryset, letter_type="ERL"
        ).render_to_pdf()

    @admin.action(description="Print Salary Certificate (For Yearly Tax Return)")
    def print_tax_salary_certificate(self, request, queryset):
        context = {"financial_year": FinancialYear.objects.filter(active=True).first()}
        return self.generate_pdf(
            request, queryset=queryset, letter_type="ESC", context=context
        ).render_to_pdf()

    @admin.action(description="Print Salary Certificate (Last month)")
    def print_salary_certificate(self, request, queryset):
        return self.generate_pdf(
            request, queryset=queryset, letter_type="ELMSC"
        ).render_to_pdf()

    @admin.action(description="Print Salary Certificate (All months)")
    def print_salary_certificate_all_months(self, request, queryset):
        # employee_ids = queryset.values_list('id', flat=True)
        # employee_salarys = EmployeeSalary.objects.filter(employee__id__in=employee_ids)

        # for salary in employee_salarys:

        return self.generate_pdf(
            request, queryset=queryset, letter_type="EAMSC"
        ).render_to_pdf()

    @admin.action(description="Print Salary Account Forwarding Letter")
    def print_bank_forwarding_letter(self, request, queryset):
        return self.generate_pdf(
            request, queryset=queryset, letter_type="AFL"
        ).render_to_pdf()

    @admin.action(description="Print Experience Letter")
    def print_experience_letter(self, request, queryset):

        return self.generate_pdf(
            request, queryset=queryset, letter_type="EXPL"
        ).render_to_pdf()
        
        
    @admin.action(description="Mail Role Change Letter")
    def mail_role_change_letter(self, request, queryset):
        print(config.settings.STATIC_URL)
        promotion_policy_file = f"{config.settings.STATIC_URL}stationary/Employee-hierarchy-plan-for-mediusware-ltd.pdf"
        
        for employee in queryset:
            html_context = loader.render_to_string(
            "mails/role_update.html", context={"employee": employee}
        )
            email_send_to_employee(employee, promotion_policy_file, html_context, "Your Updated Role and Growth Path at Mediusware Ltd.")
            # async_task(
            #         "employee.tasks.role_change_email_send_to_employee",
            #         employee,
            #         promotion_policy_file,
            #         html_context,
            #         "Your Updated Role and Growth Path at Mediusware Ltd.",
            #     )
            
    
    @admin.action(description="Mail Promotion Letter")
    def mail_promotion_letter(self, request, queryset):
        promotion_policy_file = f"{config.settings.STATIC_URL}stationary/Employee-hierarchy-plan-for-mediusware-ltd.pdf"
        for employee in queryset:
            html_context = loader.render_to_string(
                "mails/promotion.html", context={"employee": employee}
            )
            email_send_to_employee(employee, promotion_policy_file, html_context, "Congratulations on Your Promotion at Mediusware Ltd.")
            # async_task(
            #     "employee.tasks.role_change_email_send_to_employee",
            #     employee,
            #     promotion_policy_file,
            #     html_context,
            #     "Congratulations on Your Promotion at Mediusware Ltd.",
            # )
        
    
    @admin.action(description="Mail Appointment Letter")
    def mail_appointment_letter(self, request, queryset):
        hr_policy = (
            HRPolicy.objects.filter(active=True)
            .order_by("-created_at")
            .prefetch_related("hrpolicysection_set")
            .first()
        )
        if not hr_policy:
            hr_policies = []
        else:
            hr_policies = hr_policy.policy_file

        # policy_file =

        self.__send_mail(
            queryset,
            letter_type="EAL",
            subject="Appointment letter",
            # mail_template=["mails/appointment.html", "mails/appointment.html"],
            mail_template="mails/appointment.html",
            # extra_context={"hr_policies": hr_policies},
            request=request,
        )
        # for employee in queryset:
        #     async_task(
        #             "employee.tasks.send_mail_to_employee",
        #             employee,
        #             pdf = ["mails/appointment.html", "mails/appointment.html"],
        #             html_body =
        #             subject,
        #         )

    @admin.action()
    def mail_permanent_letter(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type="EPL",
            subject="Permanent letter",
            mail_template="mails/permanent.html",
            request=request,
        )

    @admin.action
    def mail_increment_letter(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type="EIL",
            subject="Increment letter",
            mail_template="mails/increment.html",
            request=request,
        )

    @admin.action(description="Mail NOC letter")
    def mail_noc_letter(self, request, queryset):
        self.__send_mail(
            queryset=queryset,
            letter_type="NOC",
            subject="No Objection Certificate (NOC)",
            mail_template="mails/noc.html",
            request=request,
        )

    @admin.action()
    def mail_salary_certificate(self, request, queryset):
        self.__send_mail(
            queryset,
            letter_type="ESC",
            subject="No objection certificate (NOC)",
            mail_template="mails/noc.html",
            request=request,
        )

    @admin.action(description="Download all active employee information")
    def download_employee_info(self, request, queryset):
        wb = Workbook()
        work_sheets = {}
        work_sheet = wb.create_sheet(title="Employee List")
        work_sheet.append(
            ["Name", "Designation", "Phone", "Email", "Address", "Date Of Birth"]
        )
        for employee in Employee.objects.filter(active=True).all():
            work_sheet.append(
                [
                    employee.full_name,
                    employee.designation.title,
                    employee.phone,
                    employee.email,
                    employee.address,
                    employee.date_of_birth,
                ]
            )
        work_sheets["employee"] = work_sheet
        wb.remove(wb["Sheet"])
        response = HttpResponse(
            content=save_virtual_workbook(wb), content_type="application/ms-excel"
        )
        response["Content-Disposition"] = "attachment; filename=Employees.xlsx"
        return response

    def __send_mail(
        self,
        queryset,
        letter_type,
        subject,
        mail_template,
        request,
        extra_context: dict = {},
    ):
        for employee in queryset:
            note = employee.salaryhistory_set.first().note
            extra_context["note"] = note
            pdf = self.generate_pdf(
                request,
                queryset=(employee,),
                letter_type=letter_type,
                extra_context=extra_context,
            ).create()
            print(pdf)
            print(type(pdf))
            # pdf = [pdf, pdf]
            enoc = EmployeeNOC.objects.filter(employee_id=employee.id)
            if letter_type == "NOC":
                if enoc.exists():
                    enoc = enoc.first()
                    if pdf.__contains__("http"):
                        file_obj = requests.get(pdf).content
                        file_name = pdf.split("/")[-1]
                        image_name = file_name[:-4] + ".jpg"
                        enoc.noc_pdf.save(file_name, ContentFile(file_obj, file_name))
                        image_file = pdf2image.convert_from_bytes(file_obj)[0]
                        image_io = BytesIO()
                        image_file.save(image_io, format="jpeg", quality=100)
                        enoc.noc_image.save(
                            name=image_name,
                            content=ContentFile(image_io.getvalue()),
                        )
                        enoc.save(update_fields=["noc_pdf", "noc_image"])
                    else:
                        with open(file=pdf, mode="rb") as file_obj:
                            file_name = os.path.basename(file_obj.name)
                            image_name = file_name[:-4] + ".jpg"
                            enoc.noc_pdf.save(file_name, File(file_obj, file_name))
                            image_file = pdf2image.convert_from_path(pdf)[0]
                            image_io = BytesIO()
                            image_file.save(image_io, format="jpeg", quality=100)
                            enoc.noc_image.save(
                                name=image_name,
                                content=ContentFile(image_io.getvalue()),
                            )
                            enoc.save(update_fields=["noc_pdf", "noc_image"])
            context = {
                "employee": employee,
                **extra_context,
            }
            context.update(extra_context)
            html_body = loader.render_to_string(mail_template, context=context)

            async_task(
                "employee.tasks.send_mail_to_employee",
                employee,
                pdf,
                html_body,
                subject,
                letter_type,
            )
        self.message_user(request, "Mail sent successfully", messages.SUCCESS)

    # Download generated pdf ile
    def generate_pdf(
        self, request, queryset, letter_type="EAL", context=None, extra_context={}
    ):
        qr_root = f"{config.settings.MEDIA_ROOT}/noc_qr"
        # print('qr_root', qr_root)
        try:
            os.makedirs(qr_root, exist_ok=True)
        except Exception as e:
            print(e)

        if letter_type == "NOC":
            extra_context["qr_root"] = qr_root
            for emp in queryset:
                if getattr(emp, "employeenoc", None):
                    emp_uuid = emp.employeenoc.uuid
                    qr_loc = f"{qr_root}/qr_{emp.slug}_{emp_uuid}.png"
                    url = f"{os.environ.get('NOC_VERIFY_URL')}/{emp_uuid}"
                    qr = qrcode.make(url)
                    qr.save(qr_loc)

        pdf = PDF()
        pdf.file_name = f"{self.create_file_name(queryset)}{letter_type}"
        pdf.template_path = self.get_letter_type(letter_type)
        pdf.context = {
            "employees": queryset,
            **extra_context,
            "latter_type": letter_type,
            "context": context,
            "seal": f"{config.settings.STATIC_ROOT}/stationary/sign_md.png",
        }
        return pdf

    # generate file using selected employees
    def create_file_name(self, queryset):
        file_name = ""
        for value in queryset:
            file_name += f"{slugify(value.full_name)}-"
        return file_name

    def get_letter_type(self, letter_type):
        switcher = {
            "EAL": "letters/appointment_latter.html",
            "EPL": "letters/permanent_letter.html",
            "EIL": "letters/increment_latter.html",
            "NOC": "letters/noc_letter.html",
            "ERL": "letters/resignation_letter.html",
            "ESC": "letters/salary_certificate.html",
            "ELMSC": "letters/salary_certificate_last_month.html",
            "EAMSC": "letters/salary_certificate_all_months.html",
            "AFL": "letters/salary_account_forwarding_letter.html",
            "EPRL": "letters/promotion_letter.html",
            "EXPL": "letters/experience_letter.html",
            "ESPS": "letters/payslip_all_months.html",
        }
        return switcher.get(letter_type, "")
