import datetime

from django.contrib import admin

# Register your models here.
from employee.models import Employee
from .models import Designation, PayScale, LeaveManagement, PublicHoliday, PublicHolidayDate

admin.site.register(Designation)
admin.site.register(PayScale)
admin.site.register(LeaveManagement)


class PublicHolidayDateInline(admin.TabularInline):
    model = PublicHolidayDate
    extra = 1


@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    inlines = (PublicHolidayDateInline,)
    list_display = ('title', 'days')

    def days(self, obj):
        total_days = obj.public_holiday.count()
        date_list = [dt for dt in obj.public_holiday.values_list('date', flat=True)]
        print(date_list)
        return "({}) \n {}".format(total_days, date_list)
