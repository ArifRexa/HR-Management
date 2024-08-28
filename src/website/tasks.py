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
    email.from_email = '"Mediusware-Admin" <admin@mediusware.com>'
    email.send()


def thank_you_message_to_author(blog: Blog, url):
    employee = blog.created_by.employee
    html_template = get_template("blog/mail/author_thank_you.html")
    html_content = html_template.render(
        {"employee": employee, "blog": blog, "url": url}
    )

    email = EmailMultiAlternatives(
        subject="Mediusware Blog - Thank You for Your Contribution!"
    )
    email.attach_alternative(html_content, "text/html")
    email.to = [employee.email]
    email.from_email = '"Mediusware-Admin" <admin@mediusware.com>'
    email.send()


def automatic_blog_post_linkedin():
    blog_base_url = "https://mediusware.com/"
    banner_image_base_url = "https://hr.mediusware.xyz/"

    blog = (
        Blog.objects.filter(
            status=BlogStatus.APPROVED, is_posted=False, approved_at__isnull=False
        )
        .order_by("approved_at")
        .first()
    )
    print(blog)
    token = PostCredential.objects.filter(platform=PostPlatform.LINKEDIN).first()

    # Example usage

    # access_token ='AQXxdlhuPelMDabM9X6o0l9C77gaydO_XNXrtollPXt3oPyU1VXFVsgGBzPZ3wIJb27bcbITcbtOnKCTSwqOAp5HzSxwsIa3MWusJAXiAeiK4SfvtwXelxgH6YxAtiM6ismk19d8gElpNv7itx5npOhAIjR_TkpGFFBG6-Km7_ECJfbludRlEUwJ9ppzfJzbSXkJ857opBrSa0XntUYlPEs_SXtWrpGnfLiy80eYrkYE0NrsdusTd8nr4J7lu7PKn4kkn7eGIzkhcWszGRChQHKmpGmWBsSfdm-LJ_C_SqAja0jIGZzZ14xITNWQahjvEmj0USXULIDBASujJSOBOosBPXebEA'
    access_token = token.token

    # for blog in blogs_activated_today:
    title = blog.title

    # categories_with_hashtags = "  ".join(f"#{category.name.replace(' ', '_')}" for category in blog.category.all())
    # description_with_categories = f"{description}\n\n{categories_with_hashtags}"
    blog_url = f"{blog_base_url}blog/details/{blog.slug}"
    description = strip_tags(blog.content)
    thumbnail = f"{banner_image_base_url}{blog.image.url}"
    try:
        print("posting start")
        LinkedinAutomate(
            access_token,
            blog_url,
            title,
            description,
            thumbnail,
        ).main_func()
        print("posting end")
        blog.is_posted = True
        blog.save()
    except Exception as e:
        print(e)
