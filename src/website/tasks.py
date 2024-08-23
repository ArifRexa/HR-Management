from django.core.mail import EmailMultiAlternatives

from django.template.loader import get_template

from website.models import BlogModeratorFeedback


def send_blog_moderator_feedback_email(content, blog: BlogModeratorFeedback, url):
    employee = blog.created_by.employee
    html_template = get_template("blog/mail/moderator_feedback.html")
    html_content = html_template.render(
        {"content": content, "employee": employee, "blog": blog, "url": url}
    )

    email = EmailMultiAlternatives(subject="Mediusware Blog - Feedback From Moderator")
    email.attach_alternative(html_content, "text/html")
    email.to = [employee.email]
    email.from_email = '"Mediusware-Admin" <admin@mediusware.com>'
    email.send()


def thank_you_message_to_author(blog: BlogModeratorFeedback, url):
    employee = blog.created_by.employee
    html_template = get_template("blog/mail/author_thank_you.html")
    html_content = html_template.render(
        {"employee": employee, "blog": blog, "url": url}
    )

    email = EmailMultiAlternatives(subject="Mediusware Blog - Thank You for Your Contribution!")
    email.attach_alternative(html_content, "text/html")
    email.to = [employee.email]
    email.from_email = '"Mediusware-Admin" <admin@mediusware.com>'
    email.send()
