from django.contrib.humanize.templatetags.humanize import intcomma, naturalday, naturaltime
from django.db.models import Sum
from django.template.loader import get_template
from django.urls import reverse
from django.utils.html import format_html

from django.contrib import admin

from employee.models import Employee


class EmployeeAdminListView:
    def employee_info(self, obj: Employee):
        html_template = get_template('admin/employee/list/employee_info.html')
        html_content = html_template.render({
            'employee': obj
        })
        return format_html(html_content)

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

    @admin.display(ordering='active', description='Status')
    def permanent_status(self, obj):
        return format_html(
            f'Active : {"<img src=/static/admin/img/icon-yes.svg />" if obj.active else "<img src=/static/admin/img/icon-no.svg />"} <br>'
            f'Permanent : {"<img src=/static/admin/img/icon-yes.svg />" if obj.permanent_date else "<img src=/static/admin/img/icon-no.svg />"}'
        )

    @admin.display(ordering='employeeskill__skill')
    def skill(self, obj):
        skill = ''
        for employee_skill in obj.employeeskill_set.all():
            skill += f'{employee_skill.skill.title} - {employee_skill.percentage}% </br>'
        return format_html(skill)

    def sum_total_leave(self, obj):
        total = obj.aggregate(total=Sum('total_leave'))['total']
        if total is None:
            return 0
        return total
