from django.db import models
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee
from django.template.defaultfilters import truncatewords



class HRReportNoteCategory(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        verbose_name = 'HR Report Note Category'
        verbose_name_plural = 'HR Report Note Categories'


class ExcuseNote(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, limit_choices_to={'active': True})
    category = models.ForeignKey(
        HRReportNoteCategory, 
        on_delete=models.CASCADE,
        null=True, blank=False, 
        limit_choices_to={'active': True},
    )
    excuse_acts = models.TextField()

    def __str__(self) -> str:
        return f"{self.employee.full_name}"

    # def short_excuse_acts(self):
    #     return truncatewords(self.excuse_acts, 10)
    
    class Meta:
        verbose_name = 'HR Report note'
        verbose_name_plural = 'HR Report notes'


class ExcuseNoteAttachment(TimeStampMixin, AuthorMixin):
    excuse_note = models.ForeignKey(ExcuseNote, on_delete=models.CASCADE)
    attachment = models.FileField(help_text='Image , PDF or Docx file ')
