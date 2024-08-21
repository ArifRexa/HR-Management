from django.core.mail import EmailMultiAlternatives

from django.template.loader import get_template


def send_blog_moderator_feedback_email(content, employee):
    html_template = get_template("blog/mail/moderator_feedback.html")
    html_content = html_template.render({"content": content, "employee": employee})

    email = EmailMultiAlternatives(subject="Mediusware Blog - Feedback From Moderator")
    email.attach_alternative(html_content, "text/html")
    email.to = [employee.email]
    email.from_email = "Mediusware Ltd. <no-reply@mediusware.com>"
    email.send()
