from django.db import models
from tinymce.models import HTMLField
from config.model.TimeStampMixin import TimeStampMixin
from project_management.models import Technology

# Create your models here.


class MarketingSlider(TimeStampMixin):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField()
    image = models.ImageField(upload_to="marketing_slider")

    def __str__(self):
        return self.title if self.title else str(self.id)


class Training(TimeStampMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="training", null=True, blank=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title if self.title else str(self.id)


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
    description = models.TextField(null=True, blank=True)
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
    description = HTMLField()

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
