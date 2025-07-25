from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee



class HRReportNoteCategory(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        verbose_name = 'HR Report Note Category'
        verbose_name_plural = 'HR Report Note Categories'


class ExcuseNote(AuthorMixin, TimeStampMixin):
    SEVERITY_CHOICES = (
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        )
    STATUS = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved')
    )
    incedent_date = models.DateField(help_text='Date of the incident', null=True, blank=True, verbose_name='incident_date',)
    reported_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reported_excuse_notes', null=True, blank=True)
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='low',
        help_text='Severity of the incident',
        null=True, blank=True
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, limit_choices_to={'active': True})
    category = models.ForeignKey(
        HRReportNoteCategory, 
        on_delete=models.CASCADE,
        null=True, blank=False, 
        limit_choices_to={'active': True},
    )
    excuse_acts = models.TextField()
    action_taken = models.TextField(blank=True, null=True, help_text='Actions taken to resolve the incident')
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending',
        help_text='Status of the excuse note',
        null=True, blank=True
    )

    

    def __str__(self) -> str:
        return f"{self.employee.full_name}"

    # def short_excuse_acts(self):
    #     return truncatewords(self.excuse_acts, 10)
    
    class Meta:
        verbose_name = 'HR Report Note'
        verbose_name_plural = 'HR Report Notes'


class ExcuseNoteAttachment(TimeStampMixin, AuthorMixin):
    excuse_note = models.ForeignKey(ExcuseNote, on_delete=models.CASCADE)
    attachment = models.FileField(help_text='Image , PDF or Docx file ')
