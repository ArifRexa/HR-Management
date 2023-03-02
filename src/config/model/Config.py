from django.db import models

class Config(models.Model):
    qc_bonus_amount = models.PositiveIntegerField(verbose_name="QC Bonus Ratio", default=10)