from django.contrib import admin, messages

from employee.models import EmployeeNeedHelp, NeedHelpPosition


@admin.register(NeedHelpPosition)
class NeedHelpPositionAdmin(admin.ModelAdmin):
    search_fields = (
        "title",
        "email",
    )

    def has_module_permission(self, request):
        return False


# @admin.register(EmployeeNeedHelp)
# class EmployeeNeedHelpAdmin(admin.ModelAdmin):
#     list_display = (
#         "employee",
#         # "need_help_position",
#         # "active",
#     )
#     autocomplete_fields = (
#         "employee",
#         "need_help_position",
#     )



from functools import update_wrapper
import datetime
import math

from django.contrib import admin, messages
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from django.db.models import Prefetch, Count, Q

# Needed for optional Features
# from django.db.models import Count, Case, When, Value, BooleanField
from django.shortcuts import redirect
from openpyxl import Workbook

from employee.models import (
    EmployeeAttendance,
    Employee,
    PrayerInfo,
)

from employee.forms.prayer_info import EmployeePrayerInfoForm


from config.settings import employee_ids as management_ids







#base admin class for this all model

def sToTime(duration):
    minutes = math.floor((duration / 60) % 60)
    hours = math.floor((duration / (60 * 60)) % 24)

    return f"{hours:01}h: {minutes:01}m"



