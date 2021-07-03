from datetime import date

from django.contrib.humanize.templatetags.humanize import intcomma, naturalday
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils.timesince import timesince
from xhtml2pdf import pisa

from config.utils import link_callback


class EmployeeAdmin:
    def employee_info(self, obj):
        resigned = obj.resignation_set.filter(status='approved')
        return format_html(
            f'<b>Name &emsp; &emsp; &nbsp:  {obj.full_name.capitalize()} </b><br>'
            f'<b>Designation :</b> {obj.designation} <br>'
            f'<b>Joined at &emsp;&nbsp;:</b> {naturalday(obj.joining_date)} <br>'
            f'{"<b>Resign at &emsp;&nbsp;:</b> " + resigned.first().date if resigned.first() else ""}'
        )

    def leave_info(self, obj):
        approved_leave = obj.leave_set.filter(status='approved')
        return format_html(
            f"<b>Casual &emsp;:</b> <b>{self.sum_total_leave(approved_leave.filter(leave_type='casual'))}</b> out of {obj.leave_management.casual_leave} <br>"
            f"<b>Medical &ensp;:</b> <b>{self.sum_total_leave(approved_leave.filter(leave_type='medical'))}</b> out of {obj.leave_management.medical_leave}<br>"
            f"<b>Non Paid :</b> {self.sum_total_leave(approved_leave.filter(leave_type='non_paid'))}<br>"
        )

    def salary_history(self, obj):
        history = ''
        for salary in obj.salaryhistory_set.order_by('-active_from').all():
            history += f'<b>{intcomma(salary.payable_salary)}</b> activated from {naturalday(salary.active_from)} <br>'
        return format_html(history)

    def permanent_status(self, obj):
        if obj.permanent_date:
            return format_html(f'<img src="/static/admin/img/icon-yes.svg" />')
        return format_html(f'<img src="/static/admin/img/icon-no.svg" />')

    def sum_total_leave(self, obj):
        total = obj.aggregate(total=Sum('total_leave'))['total']
        if total is None:
            return 0
        return total

    def print_pdf(self, queryset, letter_type):
        template_path = self.get_letter_type(letter_type)
        context = {'employees': queryset, 'latter_type': letter_type}
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{letter_type}.pdf"'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)
        try:
            pisa_status = pisa.CreatePDF(html.encode('UTF-8'),
                                         dest=response,
                                         encoding='UTF-8',
                                         link_callback=link_callback
                                         )
            return response
        except Exception:
            raise Exception

    def get_letter_type(self, letter_type):
        switcher = {
            'EAL': 'letters/appointment_latter.html',
            'EPL': 'letters/permanent_letter.html',
            'EIL': 'letters/increment_latter.html',
        }
        return switcher.get(letter_type, '')
