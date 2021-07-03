from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.text import slugify
from xhtml2pdf import pisa

from config.utils import link_callback
from config.utils.link_callback import render_to_pdf
from employee.admin_mixin.EmployeeAdmin import EmployeeAdmin
from employee.models import SalaryHistory, Employee
from employee.models.attachment import Attachment


class SalaryHistoryInline(admin.StackedInline):
    model = SalaryHistory

    def get_extra(self, request, obj=None, **kwargs):
        return 1 if not obj else 0


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(EmployeeAdmin, admin.ModelAdmin):
    inlines = (AttachmentInline, SalaryHistoryInline)
    actions = ['print_appointment_letter', 'print_permanent_letter', 'print_increment_letter']
    search_fields = ['full_name', 'email', 'salaryhistory__payable_salary']

    # change_list_template = 'admin/employee/list.html'

    def get_list_display(self, request):
        list_display = ['id', 'employee_info', 'leave_info', 'salary_history', 'permanent_status', 'active']
        if not request.user.is_superuser:
            list_display.remove('salary_history')
        return list_display

    @admin.action(description='Print Appointment Letter')
    def print_appointment_letter(self, request, queryset):
        context = {'employees': queryset, 'latter_type': 'EAL'}
        return render_to_pdf(
            self.get_letter_type('EAL'),
            context,
            f'{self.create_file_name(queryset)}EAL'
        )
        # return self.print_pdf(queryset, 'EAL')

    @admin.action(description='Print Permanent Letter')
    def print_permanent_letter(self, request, queryset):
        context = {'employees': queryset, 'latter_type': 'EPL'}
        return render_to_pdf(
            self.get_letter_type('EPL'),
            context,
            f'{self.create_file_name(queryset)}EPL'
        )
        # return self.print_pdf(queryset, 'EPL')

    @admin.action(description='Print Increment Letter')
    def print_increment_letter(self, request, queryset):
        context = {'employees': queryset, 'latter_type': 'EIL'}
        return render_to_pdf(
            self.get_letter_type('EIL'),
            context,
            f'{self.create_file_name(queryset)}EIL'
        )
        # return self.print_pdf(queryset, 'EIL')

    def create_file_name(self, queryset):
        file_name = ''
        for value in queryset:
            file_name += f'{slugify(value.full_name)}-'
        return file_name
