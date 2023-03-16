from django.db import models
from django.db.models import Sum

from tinymce.models import HTMLField

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin


class Assessment(AuthorMixin, TimeStampMixin):
    TYPE_CHOICE = (
        ('mcq', 'MCQ Examination'),
        ('written', 'Written Examination'),
        ('viva', 'Viva/Oral Examination'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    pass_percentage = models.FloatField()
    duration = models.FloatField(help_text='This duration will be in minutes')
    description = HTMLField()
    type = models.CharField(max_length=40, choices=TYPE_CHOICE, default='mcq')
    open_to_start = models.BooleanField(default=False)
    order_by = models.PositiveIntegerField(default=1)


    class Meta:
        ordering = ('-order_by', )
    
    def __str__(self):
        return self.title

    @property
    def duration_display(self):
        to_human = f'{self.duration} Minutes'
        if self.duration > 60:
            in_hour = str(round(self.duration / 60, 2)).split(".")
            to_human = f'{in_hour[0]} Hour {in_hour[1]} Minutes'
        return to_human

    @property
    def score(self):
        score = self.assessmentquestion_set.all().aggregate(Sum('score'))['score__sum']
        return score if score else 0

    @property
    def pass_score(self):
        return (float(self.score) * float(self.pass_percentage)) / 100


class AssessmentQuestion(AuthorMixin, TimeStampMixin):
    TYPE = (
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
    )
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    title = HTMLField()
    score = models.FloatField()
    type = models.CharField(max_length=20, choices=TYPE)


class AssessmentAnswer(AuthorMixin, TimeStampMixin):
    title = HTMLField()
    score = models.FloatField()
    correct = models.BooleanField(default=False)
    assessment_question = models.ForeignKey(AssessmentQuestion, related_name='answers', on_delete=models.CASCADE)
