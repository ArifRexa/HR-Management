from math import floor

from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Sum
from django.http import HttpResponse
from django.utils.html import format_html
from num2words import num2words
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from account.admin.festival_bonus.actions import FestivalBonusAction
from account.models import FestivalBonusSheet, EmployeeFestivalBonus
from account.repository.FestivalBonusSheetRepository import FestivalBonusSheetRepository


class EmployeeFestivalBonusInline(admin.TabularInline):
    model = EmployeeFestivalBonus
    extra = 0
    readonly_fields = (
        'employee',
        'amount',
    ) 
    can_delete = False
    
    def has_add_permission(self, request, obj):
        return False


@admin.register(FestivalBonusSheet)
class FestivalBonusSheetAdmin(FestivalBonusAction, admin.ModelAdmin):
    list_display = ('date', 'created_at', 'get_total', 'total_employee',)
    fields = ('date',)
    inlines = (EmployeeFestivalBonusInline,)

    def save_model(self, request, festival_bonus_sheet, form, change):
        festival_bonus = FestivalBonusSheetRepository(request.POST['date'])
        festival_bonus.save()

    @admin.display(description="Total Bonus Amount")
    def get_total(self, obj):
        total_value = EmployeeFestivalBonus.objects.filter(
            festival_bonus_sheet_id=obj.id
        ).aggregate(Sum('amount'))['amount__sum']
        return format_html(
            f'<b>{intcomma(floor(total_value))}</b> <br>'
            f'{num2words(floor(total_value)).capitalize()}'
        )

    def total_employee(self, obj):
        return obj.employeefestivalbonus_set.count()

    def has_module_permission(self, request):
        return False
