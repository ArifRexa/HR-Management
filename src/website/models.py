from typing import Iterable
from .hire_models import *  # noqa
from django.db import models

# Create your models here
from tinymce.models import HTMLField
from mptt.models import MPTTModel, TreeForeignKey


from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from project_management.models import Client, Country, Technology
from employee.models import Employee
from django.core.exceptions import ValidationError


class ServiceProcess(models.Model):
    img = models.ImageField()
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


from django.core.exceptions import ValidationError


class Industry(models.Model):
    icon = models.ImageField()
    title = models.CharField(max_length=100)
    short_description = models.TextField()
    technology = models.ManyToManyField(Technology)

    def __str__(self):
        return self.title


class Service(models.Model):
    icon = models.ImageField()
    title = models.CharField(max_length=200)
    sub_title = models.CharField(max_length=200, null=True, blank=True)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    banner_image = models.ImageField()
    feature_image = models.ImageField()
    feature = HTMLField()
    service_process = models.ManyToManyField(ServiceProcess, blank=True)
    industry = models.ManyToManyField(Industry, blank=True)
    clients = models.ManyToManyField(Client, blank=True)
    order = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ServiceContent(TimeStampMixin, AuthorMixin):
    project = models.ForeignKey(Service, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = HTMLField()
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title


class ServiceTechnology(TimeStampMixin, AuthorMixin):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    technologies = models.ManyToManyField(Technology)

    def __str__(self):
        return self.title


class Category(AuthorMixin, TimeStampMixin):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Tag(AuthorMixin, TimeStampMixin):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class BlogStatus(models.TextChoices):
    DRAFT = "draft", "In Draft"
    SUBMIT_FOR_REVIEW = "submit_for_review", "In Review"
    NEED_REVISION = "need_revision", "In Revision"
    APPROVED = "approved", "Approved"
    PUBLISHED = "published", "Published"


class Blog(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="blog_images/", verbose_name="Banner Image")
    # video = models.FileField(upload_to="blog_video", blank=True, null=True)
    youtube_link = models.URLField(
        null=True, blank=True, verbose_name="Banner Youtube Video Link"
    )
    category = models.ManyToManyField(Category, related_name="categories")
    tag = models.ManyToManyField(Tag, related_name="tags")
    # short_description = models.TextField()
    is_featured = models.BooleanField(default=False)
    content = HTMLField(verbose_name="LinkedIn Marketing Content")
    # active = models.BooleanField(default=False)
    read_time_minute = models.IntegerField(default=1)
    total_view = models.PositiveBigIntegerField(default=0, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        default=BlogStatus.DRAFT,
        choices=BlogStatus.choices,
        verbose_name="Current Status",
    )
    # is_posted = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, editable=False, blank=True)

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_featured:
            featured_blogs_count = Blog.objects.filter(is_featured=True).count()
            if featured_blogs_count >= 3:
                raise ValidationError(
                    "Only up to 3 blogs can be featured.You have already added more than 3"
                )

    class Meta:
        permissions = [
            ("can_approve", "Can Approve"),
            ("can_view_all", "Can View All Employees Blog"),
            ("can_change_after_approve", "Can Change After Approve"),
            ("can_delete_after_approve", "Can Delete After Approve"),
        ]


class PostPlatform(models.TextChoices):
    LINKEDIN = "linkedin", "Linkedin"
    FACEBOOK = "facebook", "Facebook"


class PostCredential(TimeStampMixin, AuthorMixin):
    name = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(
        max_length=255, choices=PostPlatform.choices, default=PostPlatform.LINKEDIN
    )
    token = models.TextField()

    def __str__(self):
        return self.name or str(self.id)


class BlogContext(AuthorMixin, TimeStampMixin):
    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name="blog_contexts"
    )
    title = models.CharField(null=True, blank=True, max_length=255)
    description = HTMLField(null=True, blank=True)
    image = models.ImageField(upload_to="blog_context_images", blank=True, null=True)
    video = models.URLField(blank=True, null=True, verbose_name="YouTube Video Link")


class BlogFAQ(AuthorMixin, TimeStampMixin):
    blogs = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="blog_faqs")
    question = models.CharField(max_length=255)
    answer = models.TextField()


class BlogModeratorFeedback(AuthorMixin, TimeStampMixin):
    MODERATOR_FEEDBACK_TITLE = (
        (1, "Moderator"),
        (2, "Author"),
    )
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    feedback = HTMLField()
    created_by_title = models.IntegerField(
        choices=MODERATOR_FEEDBACK_TITLE, verbose_name="Created By", null=True
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.created_by == self.blog.created_by:
            self.created_by_title = 2
        else:
            self.created_by_title = 1
        super().save(*args, **kwargs)


class BlogCategory(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class BlogTag(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class BlogComment(MPTTModel, TimeStampMixin):
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    content = models.TextField()
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="comments",
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
    )


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Question")
    answer = models.TextField(verbose_name="Answer")

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"


class OurAchievement(models.Model):
    title = models.CharField(max_length=200)
    number = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="achievement", null=True, blank=True)


class OurGrowth(models.Model):
    title = models.CharField(max_length=200)
    number = models.CharField(max_length=100)


class OurJourney(models.Model):
    year = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    description = models.TextField()
    img = models.ImageField()


class EmployeePerspective(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)


class Lead(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    file = models.FileField(upload_to='leads_file/',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True) 
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True) 
    def __str__(self):
        return self.name


class Gallery(TimeStampMixin):
    image = models.ImageField(upload_to="gallery_images/")

    def __str__(self):
        return str(self.id)


class Award(TimeStampMixin):
    title = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="award_images/")
    short_description = models.TextField(null=True, blank=True)
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title or str(self.id)


class VideoTestimonial(TimeStampMixin):
    name = models.CharField(max_length=255)
    video = models.URLField()
    client_image = models.ImageField(
        upload_to="video_testimonial/client_images/", null=True, blank=True
    )
    thumbnail = models.ImageField(upload_to="video_testimonial/thumbnails/")
    description = models.TextField(blank=True, null=True)
    designation = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.name


class IndustryWeServe(TimeStampMixin):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="industry_we_serve/")
    slug = models.SlugField(unique=True, null=True)


class LifeAtMediusware(TimeStampMixin):
    image = models.ImageField(upload_to="life_at_mediusware/")


class OfficeLocation(TimeStampMixin):
    office = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=255)
    image = models.ImageField(upload_to="office_location/")
    email = models.EmailField(null=True, blank=True)

    def __str__(self, *args, **kwargs):
        return self.office


class Brand(models.Model):
    brandphoto = models.ImageField(upload_to='brand_photos/')
    
    def __str__(self):
        return f"Brand {self.id}"