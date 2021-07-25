import datetime

from django.contrib import admin

# Register your models here.
from django.template.defaultfilters import truncatewords, truncatechars, truncatechars_html
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from config.utils.pdf import PDF
from employee.models import Employee
from .models import Designation, PayScale, LeaveManagement, PublicHoliday, PublicHolidayDate, Bank, Letter

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


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'default')


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_header', 'get_body', 'get_footer')
    actions = ('download_pdf',)

    @admin.display(description='Header')
    def get_header(self, obj):
        safe_value = strip_tags(truncatechars_html(obj.header, 50))
        return mark_safe("&nbsp;".join(safe_value.split(' ')))

    @admin.display(description='Body')
    def get_body(self, obj):
        safe_value = strip_tags(truncatechars_html(obj.body, 200))
        return mark_safe("&nbsp;".join(safe_value.split(' ')))

    @admin.display(description='footer')
    def get_footer(self, obj):
        safe_value = strip_tags(truncatechars_html(obj.footer, 20))
        return mark_safe("&nbsp;".join(safe_value.split(' ')))

    @admin.action(description='Print PDF')
    def download_pdf(self, request, queryset):
        pdf = PDF()
        pdf.template_path = 'letter.html'
        pdf.context = {'letters': queryset}
        return pdf.render_to_pdf()

    def print_pdf(self, request, queryset):
        pass
