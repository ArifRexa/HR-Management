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
from django.db.models import Sum


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
    report_send_date = datetime(2024, 12, 1)
    report_date = report_send_date - timedelta(days=1)
    month_start = datetime(report_date.year, report_date.month, 1).date()
    month_end = report_date.date()
    expenses = (
        Expense.objects.filter(date__gte=month_start, date__lte=month_end)
        .prefetch_related("expanseattachment_set")
        .order_by("-amount")
    )
    str_month = report_date.strftime("%B")
    pdf = PDF()
    pdf.file_name = f"Expanse_Report_{str_month}"
    pdf.template_path = "mail/expense_report.html"
    pdf.context = {
        "expenses": expenses,
        "seal": f"{STATIC_ROOT}/stationary/sign_md.png",
        "date": report_date,
        "total_amount": expenses.aggregate(total_amount=Sum("amount"))["total_amount"],
    }
    # Send email
    email = EmailMessage(
        subject=f"Monthly Expense Report[{str_month}/{report_date.year}]",
        body=f"Please find the attached Expense Report of {str_month}/{report_date.year}.",
        from_email='"Mediusware HR" <hr@mediusware.com>',
        to=["shahinur@mediusware.com"],
    )

    file_path = pdf.create()
    if file_path:
        if file_path.__contains__("http"):
            pdf_url = file_path

            # Fetch the PDF content from the URL
            response = requests.get(pdf_url)

            email.attach(file_path.split("/")[-1], response.content, "application/pdf")
        else:
            email.attach_file(file_path, "application/pdf")
    email.send()
