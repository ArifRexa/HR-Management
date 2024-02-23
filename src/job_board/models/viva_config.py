from django.db import models
from ..models.job import Job


class VivaConfig(models.Model):
    # job_post = models.CharField(max_length=100)
    job_post = models.ForeignKey(Job, on_delete=models.CASCADE)
    duration = models.PositiveIntegerField()  # Duration in minutes
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.job_post}"
        # return f"{self.job_post} - {self.start_date} {self.start_time} to {self.end_date} {self.end_time}"
