import calendar
from dateutil.relativedelta import relativedelta
from typing import List
from django.utils import timezone
import requests
from employee.models import Employee
from provident_fund.models import Account
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from .models import Expense, Income
from project_management.models import ProjectHour, Client
from config.settings import STATIC_ROOT
from config.utils.pdf import PDF
from django.db.models import Q


# Seed pf account
def create_all_pfaccount():
    now = timezone.now().date().replace(day=1)

    now = now - relativedelta(days=1)
    starting_date_of_pf_account = now.replace(day=1)

    maturity_date = starting_date_of_pf_account + relativedelta(years=2)

    employees = Employee.objects.filter(active=True, pf_eligibility=True)
    accounts = list()

    for employee in employees:
        accounts.append(
            Account(
                employee=employee,
                start_date=starting_date_of_pf_account,
                maturity_date=maturity_date,
                scale=10.0,
            )
        )

    Account.objects.bulk_create(accounts)


def turn_off_all_employee_pf_eligibility():
    Employee.objects.filter(pf_eligibility=True).update(pf_eligibility=False)


def create_income_from_last_week_projects():
    # Get today's date
    today = datetime.today().date()

    # Calculate yesterday's date
    yesterday = today - timedelta(days=1)

    # Calculate the date 7 days ago from yesterday
    seven_days_ago = yesterday - timedelta(days=6)

    # Query to find ProjectHour objects within the last 7 days (from seven_days_ago to yesterday)
    project_hours = ProjectHour.objects.filter(date__range=[seven_days_ago, yesterday])

    if project_hours:
        for project_hour in project_hours:
            project = project_hour.project
            if project:
                # Create or get Income instance
                income, created = Income.objects.get_or_create(
                    project=project,
                    hours=project_hour.hours,
                    hour_rate=project.hourly_rate
                    if project.hourly_rate is not None
                    else 0.00,
                    convert_rate=90.0,
                    date=project_hour.date,
                    status="pending",
                )


def generate_attachment(incomes: List[Income]):
    pdf = PDF()
    pdf.file_name = "Income Invoice"
    pdf.template_path = "compliance/income_invoice.html"
    pdf.context = {"invoices": incomes, "seal": f"{STATIC_ROOT}/stationary/sign_md.png"}
    return pdf


def send_income_email_to_clients():
    today = datetime.today().date()
    clients = Client.objects.filter(clientinvoicedate__invoice_date=today).distinct()

    for client in clients:
        incomes = Income.objects.filter(
            is_send_clients=False, project__client=client
        ).select_related("project__client")
        pdf_file = generate_attachment(incomes)

        # Send email
        email = EmailMessage(
            subject="Income Invoice",
            body="Please find the attached income invoice.",
            from_email="admin@mediusware.com",
            to=[client.email],
            cc=client.cc_email.split(",") if client.cc_email else [],
        )

        email.attach("Income_Invoice.pdf", pdf_file.create(), "application/pdf")
        email.send()

        # Update is_send_clients to True after sending the email
        incomes.update(is_send_clients=True)


def generate_and_send_monthly_expense():
    current_data = timezone.now()
    month_start = datetime(current_data.year, current_data.month, 1).date()
    month_end = datetime(
        current_data.year,
        current_data.month,
        calendar.monthrange(current_data.year, current_data.month)[1],
    ).date()
    expenses = Expense.objects.filter(date__gte=month_start, date__lte=month_end)
    pdf = PDF()
    pdf.file_name = "Expanse_Report"
    pdf.template_path = "mail/expense_report.html"
    pdf.context = {
        "expenses": expenses,
        "seal": f"{STATIC_ROOT}/stationary/sign_md.png",
        "date": current_data.strftime("%d/%m/%Y"),
    }
    # Send email
    email = EmailMessage(
        subject="Monthly Expense Report",
        body="Please find the attached Expense Report.",
        from_email="mdborhan.st@gmail.com",
        to=["mdborhan.st@gmail.com"],
    )
    
    file_path = pdf.create()
    if file_path:
        if file_path.__contains__('http'):
            pdf_url = file_path

            # Fetch the PDF content from the URL
            response = requests.get(pdf_url)

            # email.attach_alternative(html_content, 'text/html')
            print('file name:', file_path.split('/')[-1])
            email.attach(file_path.split('/')[-1], response.content, "application/pdf")
        else:
            email.attach_file(file_path, "application/pdf")
    email.send()
