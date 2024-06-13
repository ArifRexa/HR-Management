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


class TrainingTechnology(TimeStampMixin):
    title = models.CharField(max_length=255)
    technology_name = models.ManyToManyField(Technology)

    def __str__(self):
        return self.title if self.title else str(self.id)


class Training(TimeStampMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    technology = models.ForeignKey(
        TrainingTechnology,
        related_name="trainings",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    video = models.URLField(null=True, blank=True)
    starts_at = models.TimeField(null=True, blank=True)
    ends_at = models.TimeField(null=True, blank=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title if self.title else str(self.id)


class TrainingOutline(TimeStampMixin):
    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="training_outlines"
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="training_outline")

    def __str__(self):
        return self.title if self.title else str(self.id)


class TrainingProject(TimeStampMixin):
    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="training_projects"
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="training_project")
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title if self.title else str(self.id)


class TrainingLearningTopic(TimeStampMixin):
    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="training_learning_topics"
    )
    title = models.CharField(max_length=255)
    icon = models.ImageField(upload_to="training_learning_topic")

    def __str__(self):
        return self.title


class TrainingStructure(TimeStampMixin):
    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="training_structures"
    )
    week = models.CharField(max_length=255, null=True, blank=True)
    day = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField()

    def __str__(self):
        return str(self.id)


# class TrainingStructureModule(TimeStampMixin):
#     training_structure = models.ForeignKey(TrainingStructure, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255, null=True, blank=True)
#     description = HTMLField()

#     def __str__(self):
#         return self.title if self.title else str(self.id)
