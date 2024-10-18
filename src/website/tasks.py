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
    email.from_email = '"Mediusware-Admin" <admin@mediusware.com>'
    email.send()

