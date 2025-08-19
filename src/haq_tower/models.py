from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class MotherBill(models.Model):
    date = models.DateField(default=timezone.now, help_text="The month for this bill")
    total_amount_bill = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="Total amount of the bill"
    )
    pick_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Pick unit consumption",
    )
    off_pick_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Off-pick unit consumption",
    )
    total_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        editable=False,
        help_text="Total unit consumption",
    )
    per_unit_price = models.DecimalField(
        max_digits=15, decimal_places=4, editable=False, help_text="Price per unit"
    )
    attachment = models.FileField(upload_to="bills/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pick_unit:
            self.pick_unit = 0
        if not self.off_pick_unit:
            self.off_pick_unit = 0
        self.total_unit = self.pick_unit + self.off_pick_unit
        renter_meters_total_unit = (
            RenterMeter.objects.filter(mother_bill__id=self.pk).aggregate(
                Sum("total_unit")
            )["total_unit__sum"]
            or 0
        )
        self.per_unit_price = (
            self.total_amount_bill / renter_meters_total_unit
            if renter_meters_total_unit > 0
            else 0
        )
        super().save(*args, **kwargs)

    def update_all_renter_meters(self):
        for renter_meter in RenterMeter.objects.filter(mother_bill=self):
            renter_meter.save(update_mother_bill=False)

    # renter meter total unit get under a mother meter
    def renters_total_unit(self):
        mother_total_unit = 0
        for renter_meter in RenterMeter.objects.filter(mother_bill=self):
            mother_total_unit += renter_meter.total_unit
        return mother_total_unit

    def __str__(self):
        return self.date.strftime("%Y-%m-%d")

    def formatted_date(self):
        return self.date.strftime("%Y-%m-%d")

    formatted_date.short_description = "Date"

    class Meta:
        verbose_name = "Mother Meter"
        verbose_name_plural = "Mother Meters"


class Renter(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Renter's name")
    logo = models.ImageField(
        upload_to="renter_logos/", blank=True, null=True, help_text="Renter's logo"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Renter"
        verbose_name_plural = "Renters"


class RenterMeter(models.Model):
    mother_bill = models.ForeignKey(
        MotherBill, on_delete=models.CASCADE, help_text="Select the MotherBill"
    )
    renter = models.ForeignKey(
        Renter, on_delete=models.CASCADE, help_text="Select the Renter"
    )
    previous_meter_reading = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        editable=False,
        help_text="Previous meter reading",
        null=True,
    )
    total_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        editable=False,
        null=True,
        help_text="Total unit consumption for the renter",
    )
    per_unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        editable=False,
        help_text="Price per unit",
        null=True,
    )
    total_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        editable=False,
        help_text="Total price for the renter",
        null=True,
    )
    total_current_meter_reading = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="Current meter reading", null=True
    )

    def get_current_readings(self):
        readings = self.current_readings.all().values_list(
            "current_meter_reading", flat=True
        )
        return list(readings)

    def get_current_readings_display(self):
        readings = self.get_current_readings()
        return " + ".join(str(reading) for reading in readings)

    def save(self, *args, update_mother_bill=True, **kwargs):
        # Calculate previous meter reading
        previous_meter = (
            RenterMeter.objects.filter(
                renter=self.renter, mother_bill__date__lt=self.mother_bill.date
            )
            .order_by("-mother_bill__date")
            .first()
        )

        # Save first to ensure the instance is in the database
        super().save(*args, **kwargs)

        # **Refresh the instance to fetch related CurrentMeterReading**
        self.refresh_from_db()

        # Now, self.current_readings will work properly
        total_current_readings = (
            self.current_readings.aggregate(Sum("current_meter_reading"))[
                "current_meter_reading__sum"
            ]
            or 0
        )
        self.total_current_meter_reading = total_current_readings

        # Calculate total unit and total price
        self.previous_meter_reading = (
            previous_meter.total_current_meter_reading if previous_meter else 0
        )
        self.total_unit = self.total_current_meter_reading - self.previous_meter_reading

        if self.mother_bill:
            self.per_unit_price = self.mother_bill.per_unit_price
            self.total_price = self.total_unit * self.per_unit_price

        self.mother_bill.save()
        if update_mother_bill:
            self.mother_bill.update_all_renter_meters()

        # Save again to store calculated fields
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.renter.name} - {self.mother_bill.date.strftime('%B %Y')}"

    class Meta:
        verbose_name = "Renter Meter"
        verbose_name_plural = "Renter Meters"


class CurrentMeterReading(models.Model):
    renter_meter = models.ForeignKey(
        RenterMeter, on_delete=models.CASCADE, related_name="current_readings"
    )
    current_meter_reading = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="Current meter reading"
    )
    attachment = models.FileField(upload_to="meters/", blank=True, null=True)

    def __str__(self):
        return f"Reading {self.current_meter_reading} for {self.renter_meter}"


# Signals to update total_current_meter_reading in RenterMeter
@receiver(post_save, sender=CurrentMeterReading)
@receiver(post_delete, sender=CurrentMeterReading)
def update_total_current_meter_reading(sender, instance, **kwargs):
    renter_meter = instance.renter_meter
    total_current_readings = (
        renter_meter.current_readings.aggregate(Sum("current_meter_reading"))[
            "current_meter_reading__sum"
        ]
        or 0
    )
    renter_meter.total_current_meter_reading = total_current_readings
    renter_meter.save()


# # Signals to update the per unit price of MotherBill and related RenterMeters when RenterMeter is created, updated, or deleted
# @receiver(post_save, sender=RenterMeter)
# @receiver(post_delete, sender=RenterMeter)
# def update_mother_bill_and_renter_meters(sender, instance, **kwargs):
#     mother_bill = instance.mother_bill
#     if mother_bill:
#         mother_bill.update_all_renter_meters()
#         # mother_bill.save()
