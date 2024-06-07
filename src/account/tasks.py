from dateutil.relativedelta import relativedelta
from django.utils import timezone
from employee.models import Employee
from provident_fund.models import Account
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from .models import Income
from project_management.models import ProjectHour
from config.settings import STATIC_ROOT
from config.utils.pdf import PDF

# Seed pf account
def create_all_pfaccount():
    now = timezone.now().date().replace(day=1)

    now = now - relativedelta(days=1)
    starting_date_of_pf_account = now.replace(day=1)

    maturity_date = starting_date_of_pf_account + relativedelta(years=2)
    
    employees = Employee.objects.filter(active=True, pf_eligibility=True)
    accounts = list()
    
    for employee in employees:
        accounts.append(Account(
            employee=employee,
            start_date=starting_date_of_pf_account,
            maturity_date=maturity_date,
            scale=10.0,
        ))
    
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
    project_hours = ProjectHour.objects.filter(
        date__range=[seven_days_ago, yesterday]
    )

    if project_hours:
        for project_hour in project_hours:
            project = project_hour.project
            if project:
                # Create or get Income instance
                income, created = Income.objects.get_or_create(
                    project=project,
                    hours=project_hour.hours,
                    hour_rate=project.hourly_rate if project.hourly_rate is not None else 0.00,
                    convert_rate=90.0, 
                    date=project_hour.date,
                    status="pending"
                )
                
                # Generate PDF
                pdf = PDF()
                pdf.file_name = f'Income Invoice {income.id}'
                pdf.template_path = "compliance/income_invoice.html"
                pdf.context = {
                    'invoices': [income],
                    'seal': f"{STATIC_ROOT}/stationary/sign_md.png"
                }
                pdf_file = pdf.render_to_pdf(download=False)
                
                # Send email
                email = EmailMessage(
                    subject='Income Invoice',
                    body='Please find the attached income invoice.',
                    from_email='billing@mediusware.com',
                    to=[project.client.email],
                    cc =  project.client.cc_email.split(',') if project.client.cc_email else []
                )
                
                email.attach(f'Income_Invoice_{income.id}.pdf', pdf_file, 'application/pdf')
                email.send()

                
                
