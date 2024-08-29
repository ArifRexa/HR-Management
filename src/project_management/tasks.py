from datetime import datetime, timedelta

from django.core import management
from django_q.tasks import async_task
from project_management.models import ObservationProject, Project, ProjectHour, ProjectToken
from employee.models.employee import Observation
from project_management.models import DailyProjectUpdate
from dateutil.relativedelta import relativedelta
from datetime import date
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django_q.tasks import async_task, schedule
from django.core.mail import EmailMultiAlternatives
from django.template import Context, loader
from django.db.models import Q


def mark_employee_free():
    management.call_command('mark_employee_free')

def delete_new_proj():
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        deleted_count, _ = ObservationProject.objects.filter(created_at__lt=two_weeks_ago).delete()
        deleted_employee = Observation.objects.filter(created_at__lt=two_weeks_ago).delete()



def delete_old_data(months):
    
    current_date = datetime.now()
    months_ago = relativedelta(months=months)

    target_date = current_date - months_ago

    old_data = DailyProjectUpdate.objects.filter(created_at__lt=target_date)
    old_data.delete()



def send_email_for_empty_weekly_project_hour():
   
    today = date.today()
    days_to_subtract = (today.weekday() - 4) % 7 

    previous_friday = today - timedelta(days=days_to_subtract)
    projects_with_no_hours = Project.objects.exclude(projecthour__date=previous_friday)

    for project in projects_with_no_hours:
       lead_or_managers = project.associated_employees.filter(Q(lead=True) | Q(manager=True))
       for lead_or_manager in lead_or_managers:
            email_address = lead_or_manager.email
            async_task('project_management.tasks.send_email_lead_for_weekly_project_hour',email_address,lead_or_manager)

       

def send_email_lead_for_weekly_project_hour(email_address, employee):
    
    email = EmailMultiAlternatives()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = [email_address]
    email.subject = "Reminder: Weekly Project Hour Submission"
    context = {'employee': employee}
    html_content = loader.render_to_string('mails/weekly_project_hour_reminder.html', context)
    email.attach_alternative(html_content, "text/html")
    email.send()
    
def send_email_project_hourly_rate():
    
    today = datetime.now().date()
    project_to_increase_list = []
    project_to_increase_nearby_list = []

    six_months_ago = today - relativedelta(months=6)
    five_months_20d_ago = today - relativedelta(months=5, days=20)
    
    project_to_increase = Project.objects.filter(activate_from__lte = six_months_ago)
    for project in project_to_increase:
         project_to_increase_list.append(project.title)

    project_to_increase_nearby = Project.objects.filter(
        Q(activate_from__gte=six_months_ago) &
        Q(activate_from__lte=five_months_20d_ago)
    )
    for project in project_to_increase_nearby:
         project_to_increase_nearby_list.append(project.title)
    
    email = EmailMultiAlternatives()
    email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
    email.to = ['shuyaib@mediusware.com']
    email.subject = "Project Hourly Rate Increase Notification"
    context = {'project_to_increase_list':project_to_increase_list,'project_to_increase_nearby_list': project_to_increase_nearby_list}
    
    html_content = loader.render_to_string('mails/project_hourly_rate_increase.html', context)
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_client_feedback_email():
    tokens = ProjectToken.objects.filter(project__active=True)
    for token in tokens:
        email = EmailMultiAlternatives()
        email.from_email = '"Mediusware-HR" <hr@mediusware.com>'
        email.to = [token.project.client.email]  # Replace with the client's email
        email.subject = f"Feedback Request for {token.project.title}"

        # Context for the email template
        context = {
            'project_title': token.project.title,
            'client_name': token.project.client.name,  # Adjust if necessary
            'feedback_link': f"https://staging.hr.mediusware.xyz/admin/project_management/clientfeedback/client-feedback/{token.token}/"
        }

        # Render the HTML content
        html_content = loader.render_to_string('mails/client_feedback_request.html', context)
        email.attach_alternative(html_content, "text/html")
        email.send()
