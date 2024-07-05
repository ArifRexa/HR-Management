from django.db import models
from django.utils.text import slugify

from project_management.models import Technology


class ModelMixin(models.Model):
    title = models.CharField(
        max_length=255,
        help_text="if tag exist and set it then title will be not mandatory",
    )
    sub_title = models.CharField(null=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.title and hasattr(self, "tag"):
            self.title = self.get_title
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def get_title(self):
        return self.title or f"Hire {getattr(self, 'tag')} Developers"


class Quote(ModelMixin):
    pass


class HireServiceContent(ModelMixin):
    pass


class HireService(ModelMixin):
    content = models.ManyToManyField(HireServiceContent, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="hire_service")


class HireResourceStatisticContent(ModelMixin):
    junior = models.CharField(
        max_length=100,
        verbose_name="Junior Developer",
        help_text="Statistic Value Respectively for Junior Developer",
    )
    mid = models.CharField(
        max_length=100,
        verbose_name="Mid Level Developer",
        help_text="Statistic Value Respectively for Mid Level Developer",
    )
    senior = models.CharField(
        max_length=100,
        verbose_name="Senior Developer",
        help_text="Statistic Value Respectively for Senior Developer",
    )

    def __str__(self):
        return f"{self.title}|{self.junior}|{self.mid}|{self.senior}"


class HireResourceStatistic(ModelMixin):
    content = models.ManyToManyField(
        HireResourceStatisticContent,
        related_name="statistics",
    )


class HiringProcessContent(ModelMixin):
    icon = models.ImageField(null=True, blank=True, upload_to="hiring_process_icon")


class HiringProcess(ModelMixin):
    content = models.ManyToManyField(HiringProcessContent, blank=True)


class HireEngagementContent(ModelMixin):
    icon = models.ImageField(null=True, blank=True, upload_to="hiring_engagement_icon")


class HireEngagement(ModelMixin):
    content = models.ManyToManyField(HireEngagementContent, blank=True)


class HireResourceFeature(ModelMixin):
    image = models.ImageField(null=True, blank=True, upload_to="feature_image")


class HireResourceFeatureContent(ModelMixin):
    feature = models.ForeignKey(
        HireResourceFeature,
        on_delete=models.CASCADE,
        related_name="feature_contents",
        null=True,
    )


class HireResource(ModelMixin):
    tag = models.CharField(null=True, blank=True, max_length=255)


class HireResourceFAQ(ModelMixin):
    title = models.CharField(
        max_length=255,
        default="FAQ",
    )


class FAQContent(ModelMixin):
    faq = models.ForeignKey(
        HireResourceFAQ, on_delete=models.CASCADE, related_name="faqs", null=True
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()


class HirePageStaticContent(ModelMixin):
    TYPE_CHOICES = (
        ("wct", "World Class Talent"),
        ("odt", "On Demand Team"),
    )
    icon = models.ImageField(null=True, blank=True, upload_to="hire_page")
    content_type = models.CharField(max_length=3, choices=TYPE_CHOICES, default="wct")


class WorldClassTalentManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(content_type="wct")


class OnDemandTeamManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(content_type="odt")


class WorldClassTalent(HirePageStaticContent):
    objects = WorldClassTalentManager()

    class Meta:
        proxy = True
        verbose_name = "World Class Talent"
        verbose_name_plural = "World Class Talent"


class OnDemandTeam(HirePageStaticContent):
    objects = OnDemandTeamManager()

    class Meta:
        proxy = True
        verbose_name = "On Demand Team"
        verbose_name_plural = "On Demand Team"

    def save(self, *args, **kwargs):
        self.content_type = "odt"
        super().save(*args, **kwargs)


class PricingModelManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_active=True)


class Pricing(ModelMixin):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    icon = models.ImageField(null=True, blank=True, upload_to="pricing_icon")
    is_active = models.BooleanField(default=True)
    objects = PricingModelManager()

    def __str__(self):
        return f"{self.title}"

class HirePricing(ModelMixin):
    pricing_content = models.ManyToManyField(Pricing, related_name="pricing_contents")

class HireResourceContent(ModelMixin):
    tag = models.CharField(null=True, blank=True, max_length=255)
    image = models.ImageField(null=True, upload_to="hire_resource")
    resource = models.ForeignKey(
        HireResource,
        on_delete=models.CASCADE,
        related_name="hire_resource_contents",
        verbose_name="Hire Resource",
    )
    awards = models.ManyToManyField("website.Award")
    quote = models.ForeignKey(
        Quote,
        related_name="hire_resource_contents",
        on_delete=models.CASCADE,
        null=True,
    )
    pricing = models.ForeignKey(
        HirePricing,
        related_name="hire_resource_contents",
        on_delete=models.CASCADE,
        null=True,
    )
    service = models.ForeignKey(
        HireService,
        related_name="hire_resource_contents",
        on_delete=models.CASCADE,
        null=True,
    )
    statistic = models.ForeignKey(
        HireResourceStatistic,
        related_name="hire_resource_contents",
        on_delete=models.CASCADE,
        null=True,
    )
    feature = models.ForeignKey(
        HireResourceFeature,
        related_name="hire_resource_contents",
        on_delete=models.CASCADE,
        null=True,
    )
    hire_process = models.ForeignKey(
        HiringProcess,
        related_name="hire_resource_contents",
        on_delete=models.CASCADE,
        null=True,
    )
    engagement = models.ForeignKey(
        HireEngagement,
        related_name="hire_resource_contents",
        on_delete=models.CASCADE,
        null=True,
    )
    faq = models.ForeignKey(
        HireResourceFAQ,
        related_name="hire_resource_contents",
        on_delete=models.CASCADE,
        null=True,
    )
    world_class_talent = models.ManyToManyField(
        WorldClassTalent, blank=True, related_name="world_class_talent"
    )
    on_demand_team = models.ManyToManyField(
        OnDemandTeam, blank=True, related_name="on_demand_team"
    )


class WhyWeAreContent(ModelMixin):
    pass


class WhyWeAre(ModelMixin):
    hire_resource_content = models.ForeignKey(
        HireResourceContent,
        on_delete=models.CASCADE,
        related_name="why_we_are",
        null=True,
    )
    content = models.ManyToManyField(WhyWeAreContent, blank=True)


class HireResourceTechnology(ModelMixin):
    hire_resource_content = models.ForeignKey(
        HireResourceContent, on_delete=models.CASCADE, related_name="technologies"
    )
    title = models.CharField(max_length=200)
    technologies = models.ManyToManyField(Technology)



