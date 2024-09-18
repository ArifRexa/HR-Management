import requests
import json
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.template.loader import get_template
from website.models import Blog, BlogStatus, EventCalender, EventCalenderStatus, PostCredential, PostPlatform


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
        self.linkedin_urn = "urn:li:organization:28717447"

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
        # self.user_id = self.get_user_id()
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
    banner_image_base_url = "https://mw-hr.sgp1.digitaloceanspaces.com"
    linkedin_post_base_url = "https://www.linkedin.com/feed/update/"

    blog = (
        Blog.objects.filter(status=BlogStatus.APPROVED, approved_at__isnull=False)
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
        thumbnail = f"{blog.image.url}"
        print(thumbnail)
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


class Linkedin:
    def __init__(self, access_token, image, title, description):
        self.access_token = access_token
        self.title = title
        self.image = image
        self.description = description
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        self.linkedin_urn = "urn:li:organization:28717447"

    def get_user_id(self):
        url = "https://api.linkedin.com/v2/userinfo"
        response = requests.get(url, headers=self.headers)
        jsonData = response.json()
        return jsonData["sub"]

    def feed_post(self):
        url = "https://api.linkedin.com/v2/ugcPosts"
        payload = self.common_api_call_part()
        return requests.post(url, headers=self.headers, data=payload)

    # def main_func(self):
    #     # self.user_id = self.get_user_id()
    #     feed_post = self.feed_post()
    #     print(feed_post.status_code, feed_post.json())
    #     return feed_post.status_code, feed_post.json().get("id")

    def get_image_upload_url(self):
        # try:
        #     user = self.get_user_id()
        #     if user:
        #         self.linkedin_urn = f"urn:li:person:{user}"
        # except Exception as e:
        #     print(e)
        upload_init_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self.linkedin_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }

        response = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers=self.headers,
            json=upload_init_data,
        )

        if response.status_code == 200:
            upload_info = response.json()
            upload_url = upload_info["value"]["uploadMechanism"][
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
            ]["uploadUrl"]
            asset = upload_info["value"]["asset"]
        else:
            print("Error during upload registration", response.content)

        return upload_url, asset

    def upload_image(self):
        upload_url, asset = self.get_image_upload_url()
        if self.image.url.__contains__("http"):
            res = requests.get(self.image.url)
            image_file = res.content
            response = requests.put(upload_url, data=image_file)
        else:
            image_path = self.image.path
            with open(image_path, 'rb') as image_file:
                response = requests.put(upload_url, data=image_file)
        return response.status_code, asset

    def publish_post(self):
        status, asset = self.upload_image()
        if status in [200, 201]:
            post_data = {
                "author": self.linkedin_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": self.description},
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {"text": self.title},
                                "media": asset,  # asset URN from the previous step
                                "title": {"text": self.title},
                            }
                        ],
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }
            post_response = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers=self.headers,
                json=post_data,
            )
            if post_response.status_code == 201:
                return post_response.status_code
            else:
                print("Error during post creation", post_response.text)
        else:
            print("Error during image upload", status)


def automate_posts():
    token = PostCredential.objects.filter(platform=PostPlatform.LINKEDIN).first()

    access_token = token.token
    qs = EventCalender.objects.filter(publish_date=timezone.now().date())
    for obj in qs:

        post_obj = Linkedin(access_token, obj.image, obj.title, obj.description)
        post_obj.publish_post()
        obj.publish_status = EventCalenderStatus.PUBLISHED
        obj.save()
        print("Published Post", obj.title)
