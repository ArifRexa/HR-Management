from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from config.helpers import link_callback
from employee.admin_mixin.EmployeeAdmin import EmployeeAdmin
from employee.models import SalaryHistory, Employee


class SalaryHistoryInline(admin.StackedInline):
    model = SalaryHistory

    def get_extra(self, request, obj=None, **kwargs):
        return 1 if not obj else 0


@admin.register(Employee)
class EmployeeAdmin(EmployeeAdmin, admin.ModelAdmin):
    inlines = (SalaryHistoryInline,)
    actions = ['print_appointment_latter']
    search_fields = ['full_name', 'email', 'salaryhistory__payable_salary']

    # change_list_template = 'admin/employee/list.html'

    def get_list_display(self, request):
        list_display = ['id', 'employee_info', 'leave_info', 'salary_history', 'permanent_status', 'active']
        if not request.user.is_superuser:
            list_display.remove('salary_history')
        return list_display

    @admin.action(description='Print Appointment Latter')
    def print_appointment_latter(self, request, queryset):
        template_path = 'appointment_latter.html'
        context = {'employees': queryset, 'latter_type': 'EAL'}
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        try:
            pisa_status = pisa.CreatePDF(html.encode('UTF-8'), dest=response, encoding='UTF-8',
                                         link_callback=link_callback)
            return response
        except Exception:
            raise Exception
