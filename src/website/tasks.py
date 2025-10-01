from django.core.mail import EmailMultiAlternatives

from django.template.loader import get_template

from website.linkedin_post import LinkedinAutomate
from website.models import Blog, BlogStatus, PostCredential, PostPlatform
from django.utils.html import strip_tags


def send_blog_moderator_feedback_email(content, blog: Blog, url):
    employee = blog.created_by.employee
    html_template = get_template("blog/mail/moderator_feedback.html")
    html_content = html_template.render(
        {"content": content, "employee": employee, "blog": blog, "url": url}
    )

    email = EmailMultiAlternatives(subject="Mediusware Blog - Feedback From Moderator")
    email.attach_alternative(html_content, "text/html")
    email.to = [employee.email]
    email.from_email = '"Mediusware-Admin" <blog@mediusware.com>'
    email.send()


def thank_you_message_to_author(blog: Blog, url):
    employee = blog.created_by.employee
    html_template = get_template("blog/mail/author_thank_you.html")
    html_content = html_template.render(
        {"employee": employee, "blog": blog, "url": url}
    )

    email = EmailMultiAlternatives(
        subject="🎉 Congrats! Your Blog is Approved! — Enjoy a Bonus Hour!"
    )
    email.attach_alternative(html_content, "text/html")
    email.to = [employee.email]
    email.from_email = '"Mediusware-Admin" <blog@mediusware.com>'
    email.send()




from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils import timezone
from datetime import timedelta
from .models import ContactForm

def send_daily_contact_form_summary():
    # Calculate the time range: last 24 hours
    end_time = timezone.now()
    start_time = end_time - timedelta(hours=24)

    # Query ContactForm entries from the last 24 hours
    new_contacts = ContactForm.objects.filter(
        created_at__range=(start_time, end_time)
    ).order_by('-created_at')

    # If no new contacts, skip sending email
    if not new_contacts.exists():
        print("No new contact forms in the last 24 hours.")
        return

    # Prepare context for the email template
    context = {
        'new_contacts': new_contacts,
        'date_range': f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
    }

    # Render the HTML email template
    html_body = loader.render_to_string(
        'mails/daily_contact_form_summary.html',
        context=context,
    )

    # Define recipient emails (replace with actual email addresses)
    recipient_emails = ['hr@mediusware.com', 'sales@mediusware.com']

    # Create and send the email
    email = EmailMultiAlternatives(
        subject=f"Daily Contact Form Summary - {end_time.strftime('%Y-%m-%d')}",
        body="Please find the daily summary of new contact form submissions.",
        from_email='"Your Company Name" <no-reply@yourdomain.com>',
        to=recipient_emails,
    )
    email.attach_alternative(html_body, "text/html")

    try:
        email.send()
        print(f"Daily contact form summary email sent to {', '.join(recipient_emails)}")
    except Exception as e:
        print(f"Failed to send daily contact form summary email: {str(e)}")