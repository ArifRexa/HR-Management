from django.contrib import admin
from .models import Renter, MotherBill, RenterMeter, CurrentMeterReading
from config.utils.pdf import PDF
from django.template.loader import get_template
import config.settings
from num2words import num2words
from django.utils.html import format_html


def amount_in_words(amount):
    words = num2words(int(amount), lang="en_IN").title()
    words = words.replace("Euro", "Taka").replace("Cents", "Poisha")
    words = words.replace(" And ", " ")
    return words + " Taka Only"


@admin.register(MotherBill)
class MotherBillAdmin(admin.ModelAdmin):
    list_display = (
        "formatted_date",
        "total_amount_bill",
        "pick_unit",
        "off_pick_unit",
        "total_unit",
        "per_unit_price",
    )
    fields = ("date", "total_amount_bill", "pick_unit", "off_pick_unit", "attachment")
    readonly_fields = ("total_unit", "per_unit_price")
    date_hierarchy = "date"
    actions = ["print_monthly_bill"]

    # Action to print monthly bill
    @admin.action(description="Print monthly bill of Haq Tower")
    def print_monthly_bill(self, request, queryset):

        response = self.generate_pdf(
            queryset=queryset,
            letter_type="EB",
            request=request,
        )
        return response
    
    # def save_model(self, request, obj, form, change):
    #     """Override save_model to ensure calculations are performed."""
    #     obj.save()  # Calls the save method in the model
    #     obj.update_all_renter_meters()  # Update all renter meters under this MotherBill
    #     super().save_model(request, obj, form, change)

    # from num2words import num2words

    def generate_pdf(self, queryset, letter_type="EB", request=None, extra_context={}):

        mother_renters = []
        for mother_bill in queryset:
            renters = RenterMeter.objects.filter(mother_bill=mother_bill)
            for renter in renters:
                # Calculate amount in words based on total_price
                total_price = renter.mother_bill.per_unit_price*renter.total_unit
                renter.amount_in_words = amount_in_words(total_price)
                if renter.renter.logo:
                    renter.renter_logo = (
                        f"{config.settings.MEDIA_ROOT}/{renter.renter.logo}"
                    )
                else:
                    renter.renter_logo = None  # or some default URL if needed
            mother_renters.append((mother_bill, renters))

        pdf = PDF()
        pdf.file_name = self.create_file_name(queryset)
        pdf.template_path = self.get_letter_type(letter_type)

        pdf.context = {
            "mother_renters": mother_renters,
            # "bill_date": queryset.first().date,
            "letter_type": letter_type,
            "bill_bg": f"{config.settings.STATIC_ROOT}/stationary/haq_electric_bill_bg.png",
        }

        generated_pdf = pdf.render_to_pdf(download=True)
        # print("ok pdf")
        return generated_pdf

    def create_file_name(self, queryset):
        date_str = queryset.first().date.strftime("%Y-%m-%d")
        return f"haq_tower_monthly_bill_{date_str}"

    def get_letter_type(self, letter_type):
        switcher = {
            "EB": "letters/electic_bill_template.html",
        }
        return switcher.get(letter_type, "")


@admin.register(Renter)
class RenterAdmin(admin.ModelAdmin):
    list_display = ("name", "logo")
    search_fields = ("name",)
    fields = ("name", "logo")

    def has_delete_permission(self, request, obj=None):
        return True


class CurrentMeterReadingInline(admin.TabularInline):
    model = CurrentMeterReading
    extra = 1


class RenterMeterAdmin(admin.ModelAdmin):
    list_display = (
        "mother_bill",
        "renter",
        "previous_meter_reading",
        "total_current_meter_reading_details",
        "total_unit",
        "per_unit_price",
        "total_price",
    )
    fields = ("mother_bill", "renter")
    readonly_fields = (
        "previous_meter_reading",
        "total_unit",
        "per_unit_price",
        "total_price",
    )
    search_fields = ["renter__name"]
    inlines = [CurrentMeterReadingInline]

    def get_current_readings_display(self, obj):
        return obj.get_current_readings_display()

    get_current_readings_display.short_description = "Current Meter Readings"

    @admin.display()
    def total_current_meter_reading_details(self, obj):
        current_readings = obj.get_current_readings_display()
        return format_html(
            f"<p >{obj.total_current_meter_reading}</p>" f"<p >({current_readings})</p>"
        )

    # def save_model(self, request, obj, form, change):
    #     """Ensure RenterMeter calculations are updated when saving."""
    #     super().save_model(request, obj, form, change)
    #     print(obj.current_readings)
    #     obj.mother_bill.save()  # Ensure MotherBill is updated



admin.site.register(RenterMeter, RenterMeterAdmin)
# admin.site.register(CurrentMeterReading)
