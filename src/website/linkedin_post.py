import requests
import json
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

from django.template.loader import get_template
from website.models import Blog, BlogStatus, PostCredential, PostPlatform

class LinkedinAutomate:
    def __init__(self, access_token, blog_url, title, description, banner_image):
        self.access_token = access_token
        self.blog_url = blog_url
        self.title = title
        self.description = description
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        self.banner_image = banner_image

    def common_api_call_part(self, feed_type="feed", group_id=None):
        payload_dict = {
            "author": "urn:li:organization:28717447",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": self.description},
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": self.description},
                            "originalUrl": self.blog_url,
                            "title": {"text": self.title},
                            "thumbnails": [{"url": self.banner_image}],
                        }
                    ],
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                if feed_type == "feed"
                else "CONTAINER"
            },
        }

        return json.dumps(payload_dict)

    def get_user_id(self):
        url = "https://api.linkedin.com/v2/userinfo"
        response = requests.get(url, headers=self.headers)
        jsonData = response.json()
        return jsonData["sub"]

    def feed_post(self):
        url = "https://api.linkedin.com/v2/ugcPosts"
        payload = self.common_api_call_part()
        return requests.post(url, headers=self.headers, data=payload)

    def main_func(self):
        self.user_id = self.get_user_id()
        feed_post = self.feed_post()
        print(feed_post.status_code, feed_post.json())
        return feed_post.status_code, feed_post.json().get("id")

def published_email_to_blog_author(blog, url):
    employee = blog.created_by.employee
    html_template = get_template("blog/mail/blog_published.html")
    html_content = html_template.render(
        {"employee": employee, "blog": blog, "url": url}
    )

    email = EmailMultiAlternatives(
        subject="🌐 Your Blog is Now Live on LinkedIn! Share Your Success! 🚀"
    )
    email.attach_alternative(html_content, "text/html")
    email.to = [employee.email]
    email.from_email = '"Mediusware-Admin" <admin@mediusware.com>'
    email.send()
    print("email sent")

def automatic_blog_post_linkedin():
    blog_base_url = "https://mediusware.com/"
    banner_image_base_url = "https://mw-hr.sgp1.digitaloceanspaces.com/"
    linkedin_post_base_url = "https://www.linkedin.com/feed/update/"

    blog = (
        Blog.objects.filter(
            status=BlogStatus.APPROVED, approved_at__isnull=False
        )
        .order_by("approved_at")
        .first()
    )
    print(blog)
    if blog:
        token = PostCredential.objects.filter(platform=PostPlatform.LINKEDIN).first()


        access_token = token.token

        title = blog.title

        blog_url = f"{blog_base_url}blog/details/{blog.slug}"
        description = strip_tags(blog.content)
        thumbnail = f"{banner_image_base_url}{blog.image.url}"
        status, post_id = LinkedinAutomate(
                access_token,
                blog_url,
                title,
                description,
                thumbnail,
            ).main_func()
        if status == 201:
            blog.status = BlogStatus.PUBLISHED
            blog.save()
            linkedin_url = f"{linkedin_post_base_url}{post_id}"
            published_email_to_blog_author(blog, linkedin_url)

