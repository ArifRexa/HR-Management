from datetime import date

from django.contrib.humanize.templatetags.humanize import intcomma, naturalday
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils.timesince import timesince
from xhtml2pdf import pisa

from config.utils import pdf


class EmployeeAdminListView:
    def employee_info(self, obj):
        resigned = obj.resignation_set.filter(status='approved')
        return format_html(
            f'<b>Name &emsp; &emsp; &nbsp:  {obj.full_name.capitalize()} </b><br>'
            f'<b>Designation :</b> {obj.designation} <br>'
            f'<b>Joined at &emsp;&nbsp;:</b> {naturalday(obj.joining_date)} <br>'
            f'{"<b>Resign at &emsp;&nbsp;:</b> " + str(resigned.first().date) if resigned.first() else ""}'
        )

    def leave_info(self, obj):
        approved_leave = obj.leave_set.filter(status='approved')
        return format_html(
            f"<b>Casual &emsp;:</b> <b>{self.sum_total_leave(approved_leave.filter(leave_type='casual'))}</b> / {obj.leave_management.casual_leave} <br>"
            f"<b>Medical &ensp;:</b> <b>{self.sum_total_leave(approved_leave.filter(leave_type='medical'))}</b> / {obj.leave_management.medical_leave}<br>"
            f"<b>Non Paid :</b> {self.sum_total_leave(approved_leave.filter(leave_type='non_paid'))}<br>"
        )

    def salary_history(self, obj):
        history = ''
        for salary in obj.salaryhistory_set.order_by('-active_from').all():
            history += f'<b>{intcomma(salary.payable_salary)}</b> ({naturalday(salary.active_from)}) <br>'
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
