from django.db import models
from tinymce.models import HTMLField
from config.model.TimeStampMixin import TimeStampMixin
from project_management.models import Technology
from django.utils.text import slugify
# Create your models here.


class MarketingSlider(TimeStampMixin):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField()
    image = models.ImageField(upload_to="marketing_slider")

    def __str__(self):
        return self.title if self.title else str(self.id)


class Training(TimeStampMixin):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="training", null=True, blank=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title if self.title else str(self.id)

    def save(self) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save()


class TrainingTechnology(TimeStampMixin):
    training = models.ForeignKey(
        Training,
        on_delete=models.CASCADE,
        related_name="training_technologies",
        null=True,
    )
    title = models.CharField(max_length=255)
    technology_name = models.ManyToManyField(Technology)

    def __str__(self):
        return self.title if self.title else str(self.id)


class TrainingOutline(TimeStampMixin):
    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="training_outlines", null=True
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    image = models.ImageField(upload_to="training_outline")

    def __str__(self):
        return self.title if self.title else str(self.id)


class TrainingProject(TimeStampMixin):
    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="training_projects", null=True
    )
    image = models.ImageField(upload_to="training_project")

    def __str__(self):
        return str(self.id)


class TrainingLearningTopic(TimeStampMixin):
    training = models.ForeignKey(
        Training,
        on_delete=models.CASCADE,
        related_name="training_learning_topics",
        null=True,
    )
    title = models.CharField(max_length=255)
    icon = models.ImageField(upload_to="training_learning_topic")

    def __str__(self):
        return self.title


class TrainingStructure(TimeStampMixin):
    week = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.week


class TrainingStructureModule(TimeStampMixin):
    training_structure = models.ForeignKey(
        TrainingStructure,
        on_delete=models.CASCADE,
        related_name="training_modules",
        null=True,
    )
    training = models.ForeignKey(
        Training,
        on_delete=models.CASCADE,
        related_name="training_structures",
        null=True,
    )
    # day = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField(null=True, blank=True)

    def __str__(self):
        return str(self.id)


class Student(TimeStampMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    training = models.ManyToManyField(Training, related_name="students", blank=True)
    details = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="student_images", null=True, blank=True)
    file = models.FileField(upload_to="student_files")

    def __str__(self):
        return self.name


class SuccessStory(TimeStampMixin):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="success_story", null=True, blank=True)
    description = models.TextField()
    video = models.URLField()

    def __str__(self):
        return self.name


class InstructorFeedback(TimeStampMixin):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="instructor_feedback", null=True, blank=True)
    description = models.TextField()
    video = models.URLField()

    def __str__(self):
        return self.name


class HomePageWhyBest(TimeStampMixin):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="why_best")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Why We Are Best"
        verbose_name_plural = "Why We Are Best"


class OurAchievement(models.Model):
    title = models.CharField(max_length=200)
    number = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="achievement", null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    

class FAQ(TimeStampMixin):
    question = models.CharField(max_length=255, verbose_name="Question")
    answer = models.TextField(verbose_name="Answer")


    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        


class Instructor(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    image = models.ImageField(upload_to='instructors/images/',null=True,blank=True)
    designation = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=1,null=True,blank=True)  # e.g., 4.5
    short_description = models.TextField(null=True,blank=True)
    thumbnail = models.ImageField(upload_to='instructors/thumbnails/',null=True,blank=True)
    video = models.URLField(max_length=200,null=True,blank=True)

    def __str__(self):
        return self.name
    

class PracticeProject(models.Model):
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='practice_projects/',null=True,blank=True)
    short_description = models.CharField(max_length=255)
    description = models.TextField()


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class FeatureHighlight(models.Model):
    practice_project = models.ForeignKey(PracticeProject,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='feature_highlight/',null=True,blank=True) 

class TrainingProgram(TimeStampMixin):
    slug = models.SlugField(max_length=255, null=True, blank=True,editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    course_fee = models.DecimalField(max_digits=10, decimal_places=2)
    video = models.URLField(null=True,blank=True)
    image = models.ImageField(upload_to="training_image", null=True, blank=True)
    instructors = models.ManyToManyField(Instructor, related_name='training_programs')

    course_overview_subtitle = models.CharField(max_length=255,null=True,blank=True)
    course_overview_image = models.ImageField(upload_to='course_overviews/images/',null=True,blank=True)
    course_overview_description = HTMLField()

    training_reason_title = models.CharField(max_length=255,null=True,blank=True)

    training_for_title = models.CharField(max_length=255,null=True,blank=True)
    training_for_subtitle = models.TextField(null=True,blank=True)

    training_outline_title = models.CharField(max_length=255,null=True,blank=True)
    training_outline_subtitle = models.CharField(max_length=255,null=True,blank=True)

    training_tools_title =  models.CharField(max_length=255,null=True,blank=True)
    training_tools_subtitle =  models.CharField(max_length=255,null=True,blank=True)
    training_technology = models.ManyToManyField(Technology)

    project_title = models.CharField(max_length=255,null=True,blank=True)
    project_subtitle = models.CharField(max_length=255,null=True,blank=True)
    practice_projects = models.ManyToManyField(PracticeProject)

    project_showcase_title = models.CharField(max_length=255,null=True,blank=True)
    project_showcase_description = models.TextField(null=True,blank=True)

    student_review_title = models.CharField(max_length=255,null=True,blank=True)
    student_review_description = models.TextField(null=True,blank=True)

    training_faq_subtitle = models.CharField(max_length=255,null=True,blank=True)

    PROGRAM_ACTIVE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('deactivate', 'Deactivate'),
        ('pending', 'Pending'),
    ]
    program_active_status = models.CharField(
        max_length=10,
        choices=PROGRAM_ACTIVE_STATUS_CHOICES,
        default='pending'
    )

    def save(self) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save()



class TrainingReason(models.Model):
    trainingprogram = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='training_reasons')
    title = models.CharField(max_length=255,null=True,blank=True)
    image = models.ImageField(upload_to='training_reasons/images/',null=True,blank=True)

    def __str__(self):
        return self.title
    
class TrainingFor(models.Model):
    trainingprogram = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='training_for')
    icon = models.ImageField(upload_to='training_for/images/',null=True,blank=True)
    prospect = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    
class Training_Outline(models.Model):
    trainingprogram = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='trainingoutline')
    title = models.CharField(max_length=255,null=True,blank=True)
    duration = models.CharField(max_length=255,null=True,blank=True)
    description = HTMLField()


class ProjectShowcase(models.Model):
    trainingprogram = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='project_showcase')
    title = models.CharField(max_length=255,null=True,blank=True)
    video = models.URLField()
    thumbnail = models.ImageField(upload_to='projectshowcase/thumbnails/')

class StudentReview(models.Model):
    trainingprogram = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='student_review')
    title = models.CharField(max_length=255,null=True,blank=True)
    video = models.URLField()
    thumbnail = models.ImageField(upload_to='studentreview/thumbnails/')


class TrainingFAQ(models.Model):
    trainingprogram = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='training_faq')
    question = models.CharField(max_length=255, verbose_name="Question")
    answer = models.TextField(verbose_name="Answer")


    def __str__(self):
        return self.question

class PageBanner(TimeStampMixin):
    def __str__(self):
        return "Page Banner"

class AcademyBanner(TimeStampMixin):
    title = models.CharField(max_length=255, null=True, blank=True)
    sub_title = models.TextField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="academy/banner", null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    page_banner = models.OneToOneField(PageBanner, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        abstract = True

class HomeBanner(AcademyBanner):
    pass


class AllTrainingBanner(AcademyBanner):
    pass

class InstructorBanner(AcademyBanner):
    pass

class SuccessStoryBanner(AcademyBanner):
    pass