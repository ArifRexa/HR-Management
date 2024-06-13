import math

from django.db import models

# Create your models here
from tinymce.models import HTMLField
from mptt.models import MPTTModel, TreeForeignKey


from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from project_management.models import Client, Technology
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
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    banner_image = models.ImageField()
    feature_image = models.ImageField()
    feature = HTMLField()
    service_process = models.ManyToManyField(ServiceProcess)
    industry = models.ManyToManyField(Industry)
    clients = models.ManyToManyField(Client)
    order = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

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


class Blog(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="blog_images/")
    video = models.FileField(upload_to="blog_video", blank=True, null=True)
    youtube_link = models.URLField(null=True, blank=True)
    category = models.ManyToManyField(Category, related_name="categories")
    tag = models.ManyToManyField(Tag, related_name="tags")
    short_description = models.TextField()
    is_featured = models.BooleanField(default=False)
    content = HTMLField()
    active = models.BooleanField(default=False)
    read_time_minute = models.IntegerField(default=1)
    total_view = models.PositiveBigIntegerField(default=0, blank=True, null=True)

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

    def clean(self):
        if self.is_featured:
            featured_blogs_count = Blog.objects.filter(is_featured=True).count()
            if featured_blogs_count >= 3:
                raise ValidationError(
                    "Only up to 3 blogs can be featured.You have already added more than 3"
                )


class BlogContext(AuthorMixin, TimeStampMixin):
    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name="blog_contexts"
    )
    title = models.CharField(null=True, blank=True, max_length=255)
    description = HTMLField(null=True, blank=True)
    image = models.ImageField(upload_to="blog_context_images", blank=True, null=True)
    video = models.FileField(upload_to="blog_context_videos", blank=True, null=True)


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

    def __str__(self):
        return self.name


class Gallery(TimeStampMixin):
    image = models.ImageField(upload_to="gallery_images/")

    def __str__(self):
        return str(self.id)


class Award(TimeStampMixin):
    # name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="award_images/")

    def __str__(self):
        return str(self.id)
