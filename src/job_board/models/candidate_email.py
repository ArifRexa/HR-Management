from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from django.db import models
from tinymce import models as tinymce_models


class CandidateEmail(TimeStampMixin, AuthorMixin):
    subject = models.CharField(max_length=50)
    body = tinymce_models.HTMLField(null=True, blank=True)
    by_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        
        if self.by_default:
            CandidateEmail.objects.exclude(pk=self.pk).update(by_default=False)        
        super().save(*args, **kwargs)

class CandidateEmailAttatchment(TimeStampMixin, AuthorMixin):
    candidate_email = models.ForeignKey(CandidateEmail, on_delete=models.CASCADE, null=True, blank=True)
    attachments = models.FileField(upload_to='email_attachments/', null=True, blank=True)

