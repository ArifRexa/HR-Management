from tabnanny import verbose
from django.db import models
from config.model.TimeStampMixin import TimeStampMixin


class CSR(TimeStampMixin):
    title = models.CharField(max_length=255)
    short_description = models.TextField()
    banner_image = models.ImageField(upload_to="csr_images/",null=True,blank=True)

    class Meta:
        verbose_name = "CSR"
        verbose_name_plural = "CSR"

class OurEvent(TimeStampMixin):
    csr = models.ForeignKey(CSR,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="event_images/",null=True,blank=True)

class OurEffort(TimeStampMixin):
    csr = models.ForeignKey(CSR,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="effort_images/",null=True,blank=True)