import base64
import uuid
from io import BytesIO

from django.core.exceptions import ValidationError
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here
from tinymce.models import HTMLField
from weasyprint import HTML

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee
from project_management.models import Client, Country, Project, Technology
from website.models_v2.hire_resources import HireResourcePage

from .hire_models import *  # noqa


class ServiceProcess(models.Model):
    img = models.ImageField()
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


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


class BlogSlugField(models.SlugField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_length = 255


class BlogSchemaType(models.TextChoices):
    ARTICLE = "Article", "Article"
    NEWS = "NewsArticle", "News"
    HOWTO = "HowTo", "How-To"


class Blog(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    slug = BlogSlugField(unique=True)
    image = models.ImageField(upload_to="blog_images/", verbose_name="Banner Image")
    # video = models.FileField(upload_to="blog_video", blank=True, null=True)
    youtube_link = models.URLField(
        null=True, blank=True, verbose_name="Banner Video Link"
    )
    category = models.ManyToManyField(Category, related_name="categories")
    tag = models.ManyToManyField(Tag, related_name="tags")
    # short_description = models.TextField()
    is_featured = models.BooleanField(default=False)
    content = HTMLField(
        verbose_name="LinkedIn Marketing Content", blank=True, null=True
    )
    # active = models.BooleanField(default=False)
    read_time_minute = models.IntegerField(default=1, null=True, blank=True)
    total_view = models.PositiveBigIntegerField(default=0, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        default=BlogStatus.DRAFT,
        choices=BlogStatus.choices,
        verbose_name="Current Status",
    )
    # is_posted = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, editable=False, blank=True)
    schema_type = models.CharField(max_length=20, choices=BlogSchemaType.choices, default=BlogSchemaType.ARTICLE, verbose_name="Schema Type")
    main_body_schema = HTMLField(verbose_name="Main Body Schema", blank=True, null=True)
    hightlighted_text = HTMLField(
        verbose_name="Highlighted Text",
        blank=True,
        null=True,
        help_text="Text that will be highlighted in the blog content",
    )

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

    def collect_blog_content(self):
        """
        Collect all related blog content, generate a PDF file, and return it as a base64-encoded string.
        """
        sections = self.blog_contexts.all()
        full_content = ""

        for section in sections:
            # Collect title and description in HTML format
            title_html = f"<h2>{section.title or ''}</h2>" if section.title else ""
            description_html = (
                f"<p>{section.description or ''}</p>" if section.description else ""
            )

            full_content += f"{title_html} \n {description_html} \n"

        # Generate the HTML content for the PDF
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>{self.title}</title>
        </head>
        <body>
            <h1>{self.title}</h1>
            {full_content}
        </body>
        </html>
        """

        # Convert the HTML content to PDF using WeasyPrint
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)

        # Move to the beginning of the BytesIO buffer
        pdf_file.seek(0)

        # Encode the PDF file to base64
        pdf_base64 = base64.b64encode(pdf_file.read()).decode("utf-8")

        return pdf_base64


class BlogSEOEssential(TimeStampMixin, AuthorMixin):
    title = models.CharField(max_length=255, verbose_name="Meta Title")
    description = models.TextField(verbose_name="Meta Description")
    keywords = models.TextField(verbose_name="Meta Keywords")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "SEO Essential"
        verbose_name_plural = "SEO Essentials"

    def __str__(self):
        return self.title or f"SEO Essential for {self.blog.title if self.blog else 'No Blog'}"


class ReferenceBlogs(models.Model):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reference_blog",
    )
    reference_blog_title = models.CharField(max_length=200, null=True, blank=True)
    reference_blog_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.reference_blog_title

    class Meta:
        verbose_name_plural = "Reference Blogs"


class RelatedBlogs(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)
    releted_blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="releted_blog",
    )

    def __str__(self):
        return self.blog.title

    class Meta:
        verbose_name_plural = "Related Blogs"


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
    title = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Section Title"
    )
    description = HTMLField(null=True, blank=True, verbose_name="Section Description")
    image = models.ImageField(
        upload_to="blog_context_images",
        blank=True,
        null=True,
        verbose_name="Section Image",
    )
    video = models.URLField(
        blank=True, null=True, verbose_name="Section YouTube Video Link"
    )

    def __str__(self):
        return self.title or f"Context for {self.blog.title if self.blog else 'No Blog'}"


class BlogFAQ(AuthorMixin, TimeStampMixin):
    blogs = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="blog_faqs")
    question = models.CharField(max_length=255)
    answer = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.question or f"FAQ for {self.blogs.title if self.blogs else 'No Blog'}"

class BlogFAQSchema(models.Model):
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE, related_name="faq_schema")
    faq_schema = models.TextField(
        null=True, blank=True, verbose_name="FAQ Schema",
        help_text="JSON-LD format for FAQ schema, leave blank to disable schema"
    )

    class Meta:
        verbose_name = "Blog FAQ Schema"
        verbose_name_plural = "Blog FAQ Schemas"


    def __str__(self):
        return f"FAQ Schema for {self.blog.title if self.blog else 'No Blog'}"



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


class CTA(TimeStampMixin):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    button_link = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="cta_images/", null=True, blank=True)
    blog = models.ForeignKey(
        Blog, 
        on_delete=models.CASCADE, 
        related_name="ctas", 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.title or "CTA"


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
    file = models.FileField(upload_to="leads_file/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

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

    def __str__(self):
        return self.title


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
    brandphoto = models.ImageField(upload_to="brand_photos/")

    def __str__(self):
        return f"Brand {self.id}"


# Base model without any fields
class WebsiteTitle(models.Model):
    def __str__(self):
        return f"WebsiteTitle {self.pk}"  # Optional for admin display purposes


# Abstract class to reduce repetition
class BaseModelTitle(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    sub_title = models.CharField(max_length=255, null=True, blank=True)
    website_title = models.OneToOneField(WebsiteTitle, on_delete=models.CASCADE)

    class Meta:
        abstract = True


# Define all the required models with 'Title' added to the name
class AwardsTitle(BaseModelTitle):
    pass


class WhyUsTitle(BaseModelTitle):
    pass


class AllServicesTitle(BaseModelTitle):
    pass


class TechnologyTitle(BaseModelTitle):
    pass


class VideoTestimonialTitle(BaseModelTitle):  # Already has Title in the name
    pass


class IndustryTitle(BaseModelTitle):
    pass


class LifeAtMediuswareTitle(BaseModelTitle):  # Already has Title in the name
    pass


class ProjectsVideoTitle(BaseModelTitle):
    pass


class BlogTitle(BaseModelTitle):
    pass


class TextualTestimonialTitle(BaseModelTitle):  # Already has Title in the name
    pass


class SpecialProjectsTitle(BaseModelTitle):
    pass


class FAQHomeTitle(BaseModelTitle):
    pass


class OurJourneyTitle(BaseModelTitle):  # Already has Title in the name
    pass


# New model inheriting from BaseModelTitle
class ModelTitle(BaseModelTitle):
    pass


class ProjectServiceSolutionTitle(BaseModelTitle):
    pass


class ProjectKeyFeatureTitle(BaseModelTitle):
    pass


class ProjectResultsTitle(BaseModelTitle):
    pass


class ProjectScreenshotTitle(BaseModelTitle):
    pass


class ProjectTechnologyTitle(BaseModelTitle):
    pass


class ProjectClientReviewTitle(BaseModelTitle):
    pass


class EmployeeTestimonialTitle(BaseModelTitle):
    pass


class BenefitsOfEmploymentTitle(BaseModelTitle):
    pass


class PageBanner(TimeStampMixin):
    def __str__(self):
        return str(self.id)


class BannerImage(TimeStampMixin):
    image = models.ImageField(upload_to="banner_images/", null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    page_banner = models.OneToOneField(
        PageBanner, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        verbose_name = "Banner Image"
        verbose_name_plural = "Banner Images"
        abstract = True


class HomeBanner(BannerImage):
    pass


class WhyWeAreBanner(BannerImage):
    pass


class WomenEmpowermentBanner(BannerImage):
    pass


class CSRBanner(BannerImage):
    pass


class DeliveryModelBanner(BannerImage):
    pass


class EngagementModelBanner(BannerImage):
    pass


class DevelopmentMethodologyBanner(BannerImage):
    pass


class ClientTestimonialBanner(BannerImage):
    pass


class ClutchTestimonialBanner(BannerImage):
    pass


class AwardsBanner(BannerImage):
    pass


class ContactBanner(BannerImage):
    pass


class AllProjectsBanner(BannerImage):
    pass


class LeaderShipBanner(BannerImage):
    pass


class CareerBanner(BannerImage):
    pass


class Leadership(TimeStampMixin):
    title = models.CharField(max_length=255)
    sub_title = models.TextField()
    image = models.ImageField(upload_to="leadership/")

    def __str__(self):
        return self.title


class LeadershipSpeech(TimeStampMixin):
    video_url = models.URLField()
    thumbnail = models.ImageField(upload_to="leadership_speech/")
    speech = HTMLField()
    leader = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="speeches",
        limit_choices_to={"active": True},
    )
    leadership = models.ForeignKey(
        Leadership, on_delete=models.CASCADE, null=True, related_name="speeches"
    )

    def __str__(self):
        return self.leader.full_name


class EventCalenderStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    PUBLISHED = "Published", "Published"


class EventCalender(TimeStampMixin):
    title = models.CharField(max_length=255, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to="event_calender/")
    publish_date = models.DateField(verbose_name="Date")
    publish_status = models.CharField(
        max_length=10,
        choices=EventCalenderStatus.choices,
        default=EventCalenderStatus.PENDING,
    )

    def __str__(self):
        return self.title or str(self.id)

    class Meta:
        verbose_name = "Event Calender Automate"
        verbose_name_plural = "Event Calender Automate"


class Career(TimeStampMixin):
    def __str__(self):
        return f"Career {self.id}"


class EmployeeTestimonial(TimeStampMixin):
    career = models.ForeignKey(
        Career, on_delete=models.CASCADE, related_name="testimonials"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="testimonials",
        limit_choices_to={"active": True},
    )
    title = models.CharField(max_length=255)
    url = models.URLField(verbose_name="Video URL")
    thumbnail = models.ImageField(
        upload_to="testimonial/thumbnails/", null=True, blank=True
    )

    def __str__(self):
        return f"Testimonial {self.employee.full_name}"


class BenefitsOfEmployment(TimeStampMixin):
    career = models.ForeignKey(
        Career, on_delete=models.CASCADE, related_name="benefits"
    )
    title = models.CharField(max_length=255)
    icon = models.ImageField(upload_to="benefits")

    def __str__(self):
        return self.title


class PublicImage(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="public_image/")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Public Images"


class PlagiarismInfo(TimeStampMixin):
    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name="plagiarism_info"
    )
    scan_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    export_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    plagiarism_percentage = models.FloatField(blank=True, null=True)
    pdf_file = models.FileField(upload_to="plagiarism_reports/", blank=True, null=True)

    def __str__(self):
        return (
            f"Plagiarism Report for Blog: {self.blog} ({self.plagiarism_percentage}%)"
        )


class BaseMetadata(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    canonical = models.URLField(null=True, blank=True)

    class Meta:
        abstract = True


class ServiceMeatadata(BaseMetadata):
    services = models.ForeignKey(
        Service, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.title


class BlogMeatadata(BaseMetadata):
    services = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class HireResourceMetadata(BaseMetadata):
    hire_resource = models.ForeignKey(
        HireResourcePage, on_delete=models.CASCADE, null=True, blank=True
    )


class IndustryMetadata(BaseMetadata):
    service_category = models.ForeignKey(
        "ServeCategory", on_delete=models.CASCADE, null=True, blank=True
    )


class ProjectMetadata(BaseMetadata):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )


class ProjectKeyword(models.Model):
    project_keyword = models.ForeignKey(
        ProjectMetadata, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=255)


class IndustryKeyword(models.Model):
    keyword = models.ForeignKey(
        IndustryMetadata, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ServiceKeyword(models.Model):
    service_keywords = models.ForeignKey(
        ServiceMeatadata, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BlogKeyword(models.Model):
    blog_keywords = models.ForeignKey(
        BlogMeatadata, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class HireResourceKeyword(models.Model):
    hire_resource_keywords = models.ForeignKey(
        HireResourceMetadata, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BaseContact(TimeStampMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class Contact(BaseContact):

    file = models.FileField(upload_to="contact_files/", null=True, blank=True)

    def __str__(self):
        return self.name


class Inquiry(BaseContact):
    def __str__(self):
        return self.name


class Subscription(TimeStampMixin):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
