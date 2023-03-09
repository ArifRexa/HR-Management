from django.db import models

class Config(models.Model):
    qc_bonus_amount = models.PositiveIntegerField(verbose_name="QC Bonus Ratio", default=10)
    skip_lunch_amount = models.PositiveBigIntegerField(verbose_name="Number of lunch skipp from salary", default=0)


    def __str__(self) -> str:
        return 'Configuration'
    
    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super(Config, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """

        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()