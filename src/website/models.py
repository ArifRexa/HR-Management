import math

from django.db import models

# Create your models here
from tinymce.models import HTMLField

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from project_management.models import Client, Technology


class Service(models.Model):
    icon = models.ImageField()
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    banner_image = models.ImageField()
    feature_image = models.ImageField()
    feature = HTMLField()
    technologies = models.ManyToManyField(Technology)
    clients = models.ManyToManyField(Client)
    order = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

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
    image = models.ImageField(upload_to="blog_image")
    video = models.FileField(upload_to="blog_video", blank=True, null=True)
    category = models.ManyToManyField(Category, related_name="categories")
    short_description = models.TextField()
    content = HTMLField()
    active = models.BooleanField(default=False)
    read_time_minute = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs) -> None:
    #     self.read_time_minute = math.ceil(len(self.content.split(" ")) / 200)
    #     return super(Blog, self).save(*args, **kwargs)

    class Meta:
        permissions = [
            ("can_approve", "Can Approve"),
            ("can_view_all", "Can View All Employees Blog"),
            ("can_change_after_approve", "Can Change After Approve"),
        ]


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
