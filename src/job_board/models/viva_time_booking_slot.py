from django.core.exceptions import ValidationError
from django.db import models
from datetime import datetime, timedelta
from ..models import Candidate
from django.utils.translation import gettext_lazy as _
from django.contrib import admin, messages


class JobVivaTimeSlot(models.Model):
    job_post = models.ForeignKey('VivaConfig', on_delete=models.CASCADE, default=None)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField(editable=False)
    date = models.DateField()

    class Meta:
        verbose_name = "Booked Viva Slot for Candidate"

    def clean(self):
        if self.end_time is not None and self.start_time is not None:
            # Check for overlapping time slots
            conflicting_slots = JobVivaTimeSlot.objects.exclude(pk=self.pk).filter(
                job_post=self.job_post,
                candidate=self.candidate,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )
            if conflicting_slots.exists():
                conflicting_slot = conflicting_slots.first()
                conflicting_slot_info = f"Date: {conflicting_slot.date}, Time: {conflicting_slot.start_time} - {conflicting_slot.end_time}"
                raise ValidationError(
                    _('Another schedule conflicts with this time slot. Conflicting slot: %(conflicting_slot)s'),
                    params={'conflicting_slot': conflicting_slot_info},
                )

    # def save(self, *args, **kwargs):
    #     # Set duration based on associated VivaConfig
    #     self.duration = self.job_post.vivaconfig.duration
    #
    #     # Calculate the end time based on the start time and duration
    #     start_datetime = datetime.combine(datetime.today(), self.start_time)
    #     end_datetime = start_datetime + timedelta(minutes=self.duration)
    #     self.end_time = end_datetime.time()
    #
    #     self.full_clean()  # Run clean method before saving
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Set duration based on associated VivaConfig
        if self.job_post_id:
            self.duration = self.job_post.duration

            # Calculate the end time based on the start time and duration
            start_datetime = datetime.combine(datetime.today(), self.start_time)
            end_datetime = start_datetime + timedelta(minutes=self.duration)
            self.end_time = end_datetime.time()

            self.full_clean()  # Run clean method before saving
            super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"{self.viva_config.job_post} - {self.date} - {self.start_time} to {self.end_time}"





