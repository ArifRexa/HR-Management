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
from website.models_v2.industries_we_serve import ServeCategory
from website.models_v2.services import ServicePage

from .hire_models import *  # noqa
from smart_selects.db_fields import ChainedManyToManyField


class HomePage(TimeStampMixin):
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)
    button_text = models.CharField(max_length=200, blank=True, null=True)
    button_url = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.section_title
    
    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home Page"


class HomePageHeroAnimatedTitle(models.Model):
    homepage = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="hero_animated_titles")
    title = models.CharField(max_length=100)


class BeginningOfWorking(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="beginning_of_working")
    seo_title = models.CharField(max_length=100, null=True, blank=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=100, null=True, blank=True)
    secondary_title = models.CharField(max_length=100, null=True, blank=True, verbose_name="Secondary Title")
    section_description = models.TextField(null=True, blank=True)

    verbose_name = "Service Section"
    verbose_name_plural = "Service Section"
    

class IndustryWeServeHomePage(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="industry_we_serve")
    seo_title = models.CharField(max_length=255, verbose_name="SEO Title", null=True, blank=True)
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = models.TextField(null=True, blank=True)

    verbose_name = "Industry We Serve"
    verbose_name_plural = "Industries We Serve"
    


class TechStack(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="tech_stack")
    seo_title = models.CharField(max_length=255, verbose_name="SEO Title", null=True, blank=True)
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = models.TextField(null=True, blank=True)

    verbose_name = "Tech Stack"
    verbose_name_plural = "Tech Stacks"


class TestimonialsHomePage(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="testimonials")
    seo_title = models.CharField(max_length=255, verbose_name="SEO Title", null=True, blank=True)
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = models.TextField(null=True, blank=True)

    verbose_name = "Testimonials"
    verbose_name_plural = "Testimonials"


class AwardsHomePage(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="awards")
    seo_title = models.CharField(max_length=255, verbose_name="SEO Title", null=True, blank=True)
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = models.TextField(null=True, blank=True)

    verbose_name = "Awards"
    verbose_name_plural = "Awards"


class BlogsAndArticlesHomePage(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="blogs_and_articles")
    seo_title = models.CharField(max_length=255, verbose_name="SEO Title", null=True, blank=True)
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = models.TextField(null=True, blank=True)

    verbose_name = "Blogs and Articles"
    verbose_name_plural = "Blogs and Articles"

class CaseStudyHomePage(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="case_studies")
    seo_title = models.CharField(max_length=255, verbose_name="SEO Title", null=True, blank=True)
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = models.TextField(null=True, blank=True)

    verbose_name = "Case Studies"
    verbose_name_plural = "Case Studies"


class OurProcessHome(TimeStampMixin):
    home_page = models.ForeignKey(
        HomePage,
        related_name="our_process_home",
        on_delete=models.CASCADE,
        null=True,
    )
    section_title = models.CharField(max_length=200)
    section_description = HTMLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display for process steps")








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


    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


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

# ========================================================== Technology Section ======================================================
class TechnologyType(TimeStampMixin):
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        if Technology.objects.filter(name=self.name).exists():
            raise ValidationError(f"Technology with name '{self.name}' already exists.")


class Technology(TimeStampMixin):
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Title")
    # secondary_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="Secondary Title")
    slug = models.SlugField(unique=True, null=True, blank=True)
    type = models.ForeignKey(
        TechnologyType, related_name="technologies", on_delete=models.CASCADE
    )
    icon = models.ImageField(upload_to="technology_icons/", null=True, blank=True)
    featured_image = models.ImageField(upload_to="technology_featured_images/", null=True, blank=True)
    show_in_menu = models.BooleanField(
        default=False,
        help_text="If checked, this technology will be displayed in the main menu.",
    )


    # def clean(self):
    #     if Technology.objects.filter(name=self.name).exists():
    #         raise ValidationError(f"Technology with name '{self.name}' already exists.")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Technology"
        verbose_name_plural = "Technologies"

# =============Technology Solution and Services Section================
class TechnologySolutionsAndServices(TimeStampMixin):
    services = models.ForeignKey(
        Technology,
        related_name="solutions_and_services",
        on_delete=models.SET_NULL,
        null=True,
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    secondary_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="Secondary Title")
    section_description = HTMLField(blank=True, null=True)

    # def __str__(self):
    #     return self.section_title
    
    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"
    
# =============Technology Creators Quotes Section================
class TechnologyCreatorsQuotes(TimeStampMixin):
    technology = models.ForeignKey(
        Technology,
        related_name="creators_quotes",
        on_delete=models.CASCADE,
        null=True,
    )
    quote = models.TextField(blank=True, null=True)
    author_name = models.CharField(max_length=200, blank=True, null=True)
    author_designation = models.CharField(max_length=200, blank=True, null=True)
    author_image = models.ImageField(upload_to='creator_quotes_images/', blank=True, null=True)

    # def __str__(self):
    #     return self.author_name or "Creator's Quote"

class TechnologySolutionsAndServicesCards(TimeStampMixin):
    solutions_and_services = models.ForeignKey(
        TechnologySolutionsAndServices,
        related_name="cards",
        on_delete=models.CASCADE,
        null=True,
    )
    card_title = models.CharField(max_length=200, blank=True, null=True)
    card_description = HTMLField(blank=True, null=True)

    # def __str__(self):
    #     return self.card_title

# ===================Technology Services We Provide Section=====================
class ServicesWeProvide(models.Model):
    technology = models.ForeignKey(
        Technology, 
        on_delete=models.CASCADE,
        related_name='services_we_provide',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)

    # def __str__(self):
    #     return self.section_title or "Services We Provide Heading"
    
    class Meta:
        verbose_name = "Services We Provide Heading"
        verbose_name_plural = "Services We Provide Headings"


class ServicesWeProvideCards(models.Model):
    provides = models.ForeignKey(
        ServicesWeProvide, 
        on_delete=models.CASCADE,
        related_name='services_we_provide_cards',
        null=True,
        blank=True
    )
    card_title = models.CharField(max_length=200, blank=True, null=True)
    card_description = HTMLField(blank=True, null=True)

    # def __str__(self):
    #     return self.card_title

# ===================Technology EcoSystem Section=====================
class EcoSystem(models.Model):
    technology = models.ForeignKey(
        Technology, 
        on_delete=models.CASCADE,
        related_name='ecosystem',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)

    # def __str__(self):
    #     return self.section_title or "EcoSystem Heading"
    
    class Meta:
        verbose_name = "EcoSystem Heading"
        verbose_name_plural = "EcoSystem Headings"

class EcoSystemCards(models.Model):
    ecosystem = models.ForeignKey(
        EcoSystem, 
        on_delete=models.CASCADE,
        related_name='ecosystem_cards',
        null=True,
        blank=True
    )
    card_title = models.CharField(max_length=200, blank=True, null=True)
    card_description = HTMLField(blank=True, null=True)

    # def __str__(self):
    #     return self.card_title
    
class EcoSystemCardTags(models.Model):
    ecosystem_card = models.ForeignKey(
        EcoSystemCards, 
        on_delete=models.CASCADE,
        related_name='ecosystem_card_tags',
        null=True,
        blank=True
    )
    tag = models.CharField(max_length=200, blank=True, null=True)

    # def __str__(self):
    #     return self.tag

# =====================================Technology Key Things======================================

class TechnologyKeyThings(models.Model):
    technology = models.ForeignKey(
        Technology, 
        on_delete=models.CASCADE,
        related_name='KeyThings',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)

    # def __str__(self):
    #     return self.section_title or "Benefits"
    
    class Meta:
        verbose_name = "Key Things"
        verbose_name_plural = "Key Things"

class TechnologyKeyThingsQA(models.Model):
    key_things = models.ForeignKey(
        TechnologyKeyThings, 
        on_delete=models.CASCADE,
        related_name='Tech_KeyThings_cards',
        null=True,
        blank=True
    )
    card_title = models.CharField(max_length=200, blank=True, null=True)
    card_description = HTMLField(blank=True, null=True)
    # def __str__(self):
    #     return self.card_title


# ================================= Technology Why choose us =================================

class TechnologyWhyChooseUs(TimeStampMixin):
    technology = models.ForeignKey(
        Technology,
        related_name="Tech_why_choose_us",
        on_delete=models.CASCADE,
        null=True,
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)

    # def __str__(self):
    #     return self.section_title or "Why Choose Us"
    
class TechnologyWhyChooseUsCards(TimeStampMixin):
    tech_why_choose_us = models.ForeignKey(
        TechnologyWhyChooseUs,
        related_name="Tech_why_choose_us_cards",
        on_delete=models.CASCADE,
        null=True,
    )
    icon = models.ImageField(upload_to='why_choose_us_images/', blank=True, null=True)
    card_title = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display for process steps")
    # def __str__(self):
    #     return self.card_title
    
class TechnologyWhyChooseUsCardsDetails(TimeStampMixin):
    tech_why_choose_us_cards = models.ForeignKey(
        TechnologyWhyChooseUsCards,
        related_name="tech_why_choose_us_card_details",
        on_delete=models.CASCADE,
        null=True,
    )
    card_description = HTMLField(blank=True, null=True)

    # def __str__(self):
    #     return self.card_description


# ================================= Our Process of Technology =================================

class TechnologyOurProcess(models.Model):
    technology = models.ForeignKey(
        Technology, 
        on_delete=models.CASCADE,
        related_name='our_process',
        null=True,
        blank=True
    )
    section_title = models.CharField(max_length=200)
    section_description = HTMLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display for process steps")

    # def __str__(self):
    #     return self.section_title
    
    class Meta:
        verbose_name = "Our Process"
        verbose_name_plural = "Our Processes"
        ordering = ['order']

# ================================= History of Technology =================================
class HistoryOfTech(models.Model):
    technology = models.ForeignKey(
        Technology, 
        on_delete=models.CASCADE,
        related_name='history_of_tech',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)
    image = models.ImageField(upload_to="history_of_tech_images/", null=True, blank=True)

    # def __str__(self):
    #     return self.section_title    
    class Meta:
        verbose_name = "History of Technology"
        verbose_name_plural = "History of Technologies"


# ================================= Technology FAQ =================================
        
class TechnologyFAQ(models.Model):
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = HTMLField()
    order = models.PositiveIntegerField(default=0, help_text="Order of display for FAQs")

    # def __str__(self):
    #     return self.question

    class Meta:
        verbose_name = "Technology FAQ"
        verbose_name_plural = "Technology FAQs"
        ordering = ['order']


class TechnologyFAQSchema(models.Model):
    technology = models.OneToOneField(
        Technology, 
        on_delete=models.CASCADE, 
        related_name='faq_schema'
    )
    faq_schema = models.TextField(
        help_text="JSON-LD schema for FAQs"
    )

    # def __str__(self):
    #     return f"FAQ Schema for {self.technology.name}"

# =================== Technology CTA ===================
class TechnologyCTA(TimeStampMixin):
    title = models.CharField(max_length=255, null=True, blank=True)
    # description = HTMLField(null=True, blank=True)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    button_link = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="cta_images/", null=True, blank=True)
    blog = models.ForeignKey(
        Technology, 
        on_delete=models.CASCADE, 
        related_name="ctas", 
        null=True, 
        blank=True
    )

    # def __str__(self):
    #     return self.title or "CTA"


class TechnologyMetaData(models.Model):
    technology = models.ForeignKey(
        Technology, 
        on_delete=models.CASCADE, 
        related_name="metadata", 
        null=True, 
        blank=True
    )
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    # def __str__(self):
    #     return self.meta_title or f"MetaData for {self.technology.name if self.technology else 'No Technology'}"

# ========================================================== Blog Section ======================================================
class Blog(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    slug = BlogSlugField(unique=True)
    image = models.ImageField(upload_to="blog_images/", verbose_name="Banner Image")
    # video = models.FileField(upload_to="blog_video", blank=True, null=True)
    youtube_link = models.URLField(
        null=True, blank=True, verbose_name="Banner Video Link"
    )
    category = models.ManyToManyField(Category, related_name="categories", verbose_name="tags", blank=True)
    industry_details = models.ManyToManyField(ServeCategory, related_name="blogs", blank=True, verbose_name="Industry")
    parent_services = models.ManyToManyField(
        ServicePage,
        related_name="blogs_as_parent",
        limit_choices_to={"is_parent": True},
        verbose_name="Services",
        blank=True,
    )
    # child_services = models.ManyToManyField(
    #     ServicePage,
    #     related_name="blogs_as_child",
    #     verbose_name="Child Services",
    #     limit_choices_to={"is_parent": False},
    #     blank=True
    # )
    technology_type = models.ForeignKey(
        TechnologyType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Technology Type",
    )
    technology = ChainedManyToManyField(
        Technology,
        chained_field="technology_type",  # Field on Blog model to chain with
        chained_model_field="type",  # Field on Technology model to filter by
        auto_choose=False,  # Allow multiple selections without auto-choosing
        verbose_name="Technologies",
        blank=True
    )
    author = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="blogs",
        null=True,
        blank=True,
        limit_choices_to={"active": True},
    )
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
    cta_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="CTA Title")

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_featured:
            featured_blogs_count = Blog.objects.filter(is_featured=True).count()
            if featured_blogs_count >= 3:
                raise ValidationError(
                    "Only up to 3 blogs can be featured.You have already added more than 3"
                )
        
        # if self.child_services.exists():
        #     selected_parents = set(self.parent_services.values_list('id', flat=True))
        #     for child in self.child_services.all():
        #         if child.parent_id not in selected_parents:
        #             raise ValidationError(
        #                 f"Child service '{child.title}' must belong to one of the selected parent services."
        #             )

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
    # description = HTMLField(null=True, blank=True)
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
    title = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"WebsiteTitle {self.pk}"  # Optional for admin display purposes
    
    class Meta:
        verbose_name = "Website Title"
        verbose_name_plural = "Website Titles"


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
    title = models.CharField(max_length=255, null=True, blank=True)
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
    description = HTMLField(null=True, blank=True)
    speech = HTMLField(null=True, blank=True)
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


# class IndustryKeyword(models.Model):
#     keyword = models.ForeignKey(
#         IndustryMetadata, on_delete=models.CASCADE, null=True, blank=True
#     )
#     name = models.CharField(max_length=255)

#     def __str__(self):
#         return self.name


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


class ContactForm(TimeStampMixin):
    TYPE_CHOICES = (
        ("general", "General Inquiry"),
        ("discuss", "Discuss Service"),
    )
    form_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default="discuss")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    service_require = models.CharField(max_length=255, null=True, blank=True)
    project_details = models.TextField(null=True, blank=True)
    client_query = models.TextField(null=True, blank=True)  # Client Query
    attached_file = models.FileField(upload_to="contact_files/", null=True, blank=True)




class Inquiry(BaseContact):
    def __str__(self):
        return self.name


class Subscription(TimeStampMixin):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class AdditionalPages(TimeStampMixin):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    meta_title = models.CharField(max_length=255, verbose_name="Meta Title", null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name='Meta Description')

    def __str__(self):
        return self.title
    

class TeamElement(TimeStampMixin):
    additional_page = models.ForeignKey(
        AdditionalPages, 
        on_delete=models.CASCADE,
        related_name='team_elements',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=255, verbose_name="SEO Title", null=True, blank=True)
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secodary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)
    
class AdditionalPageHeroSection(TimeStampMixin):
    additional_page = models.ForeignKey(
        AdditionalPages, 
        on_delete=models.CASCADE,
        related_name='additional_page_hero_section',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=255, verbose_name="SEO Title", null=True, blank=True)
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secodary_title = models.CharField(max_length=255, null=True, blank=True)
    # slug = models.SlugField(unique=True)
    section_description = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.section_title or "Hero Section"
    
class WhatIs(TimeStampMixin):
    additional_page = models.ForeignKey(
        AdditionalPages, 
        on_delete=models.CASCADE,
        related_name='what_is_next',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=255, verbose_name="SEO Title", blank=True, null=True)
    section_title = models.CharField(max_length=255, blank=True, null=True)
    section_description = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.section_title
    
class AdditionalPageKeyThings(TimeStampMixin):
    additional_page = models.ForeignKey(
        AdditionalPages, 
        on_delete=models.CASCADE,
        related_name='additional_page_key_things',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)

    def __str__(self):
        return self.section_title

class AdditionalPageKeyThingsCards(TimeStampMixin):
    additional_page_key_things = models.ForeignKey(
        AdditionalPageKeyThings, 
        on_delete=models.CASCADE,
        related_name='additional_page_key_things_cards',
        null=True,
        blank=True
    )
    card_title = models.CharField(max_length=200, blank=True, null=True)
    card_description = HTMLField(blank=True, null=True)
    def __str__(self):
        return self.card_title
    
class AdditionalPageWhyChooseUs(TimeStampMixin):
    additional_page = models.ForeignKey(
        AdditionalPages, 
        on_delete=models.CASCADE,
        related_name='additional_page_why_choose_us',
        null=True,
        blank=True
    )
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)

    def __str__(self):
        return self.section_title or "Why Choose Us"
    
# class AdditionalPageWhyChooseUsTableHeadings(TimeStampMixin):
#     additional_page_why_choose_us = models.ForeignKey(
#         AdditionalPageWhyChooseUs,
#         related_name="additional_page_why_choose_us_table_headings",
#         on_delete=models.SET_NULL,
#         null=True,
#     )
#     heading = models.CharField(max_length=200, blank=True, null=True)
#     order = models.PositiveIntegerField(default=0, help_text="Order of display for process steps")
#     def __str__(self):
#         return self.heading



class AdditionalPageOurProcess(models.Model):
    additional_page = models.ForeignKey(
        AdditionalPages, 
        on_delete=models.CASCADE,
        related_name='our_process',
        null=True,
        blank=True
    )
    section_title = models.CharField(max_length=200, blank=True, null=True)
    section_description = HTMLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display for process steps")

    def __str__(self):
        return self.section_title
    
    class Meta:
        verbose_name = "Our Process"
        verbose_name_plural = "Our Processes"
        ordering = ['order']


class AdditionalPageFAQ(models.Model):
    additional_page = models.ForeignKey(
        AdditionalPages, 
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True
    )
    question = models.CharField(max_length=255)
    answer = HTMLField()
    order = models.PositiveIntegerField(default=0, help_text="Order of display for FAQs")

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order']

# ================================ Award Section =================================

class AwardCategory(models.Model):
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=100)
    section_description = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Award"
        verbose_name_plural = "Awards"
    
    def __str__(self):
        return self.section_title

class AwardYearGroup(models.Model):
    category = models.ForeignKey(AwardCategory, related_name='year_groups', on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.category.section_title} - {self.year}"

class Awards(models.Model):
    year_group = models.ForeignKey(AwardYearGroup, related_name='awards', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    is_featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='awards/', null=True, blank=True)
    image_url = models.URLField(max_length=500, verbose_name="Award URL", null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    

class Certification(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='certifications/', null=True, blank=True)
    image_url = models.URLField(max_length=500, verbose_name="Certification Image URL", null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=500, verbose_name="Link", null=True, blank=True)

    def __str__(self):
        return self.title
    

class ArchivePage(TimeStampMixin):
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="SEO Title")
    section_title = models.CharField(max_length=255, null=True, blank=True)
    secondary_title = models.CharField(max_length=255, null=True, blank=True)
    section_description = HTMLField(null=True, blank=True)
    image = models.ImageField(upload_to="archive_page", null=True, blank=True)
    def __str__(self):
        return self.section_title