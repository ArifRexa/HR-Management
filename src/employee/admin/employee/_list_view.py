from django.contrib.humanize.templatetags.humanize import intcomma, naturalday
from django.db.models import Sum
from django.template.loader import get_template

from django.utils import timezone
from django.utils.html import format_html
from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.db.models import Avg
from django.db.models import Q


from employee.models import Employee

from employee.models.employee_rating_models import EmployeeRating

import datetime


class EmployeeAdminListView:
    def employee_info(self, obj: Employee):
        html_template = get_template("admin/employee/list/employee_info.html")
        html_content = html_template.render({"employee": obj})
        return format_html(html_content)

    def employee_rating(self, obj: Employee):
        current_date = timezone.now()

        # Calculate the starting month for the last four months
        starting_month = (current_date.month - 3) % 12 or 12

        # Calculate the starting year for the last four months
        starting_year = (
            current_date.year - 1
            if starting_month > current_date.month
            else current_date.year
        )

        rating = (
            EmployeeRating.objects.filter(
                Q(year=starting_year, month__gte=starting_month)
                | Q(year=current_date.year, month__lte=current_date.month),
                employee_id=obj.id,
            )
            .values_list("month")
            .annotate(average_rating=Avg("score"))
            .order_by("-month")
        )

        html_template = get_template("admin/employee/list/_rating.html")
        html_content = html_template.render({"employee": obj, "ratings": rating})
        return format_html(html_content)

    @admin.display(description="Documents")
    def get_attachment(self, obj):
        attachments = obj.attachment_set.all().order_by("file_name")
        html_content_list = [
            f'<a href="{attachment.file.url}" target="_blank">{attachment.file_name}</a>'
            for attachment in attachments
        ]
        html_content = "".join(html_content_list)
        html_content = (
            "<div style='display: flex; flex-direction: column; gap: 10px; flex-wrap: wrap;'>"
            + html_content
            + "</div>"
        )
        return format_html(html_content)

    def tour_allowance(self, obj):
        html_template = get_template("admin/employee/list/tour_allowance.html")
        today = datetime.date.today()
        first_day_of_this_month = timezone.now().replace(day=1)
        first_day_of_next_month = (
            first_day_of_this_month + datetime.timedelta(days=32)
        ).replace(day=1)
        first_day_of_twelve_months_ago = first_day_of_next_month - relativedelta(
            years=1
        )
        joining_date = obj.joining_date
        employee_tour_allowance_per_year = 1000
        total_days_from_joing = (today - joining_date).days
        years = total_days_from_joing // 365
        months = (total_days_from_joing - years * 365) // 30
        total_months = years * 12 + months
        last_day_of_twelve_months_ago_from_complete_a_year = (
            first_day_of_this_month - relativedelta(months=months)
        )
        tour_list = obj.tourallowance_set.filter(
            tour_date__range=[last_day_of_twelve_months_ago_from_complete_a_year, today]
        )
        days = total_days_from_joing - years * 365 - months * 30
        total_month_from_joing = round(total_days_from_joing / 30)
        total_cost = tour_list.aggregate(total=(Sum("expense_per_person"))).get("total")
        if total_cost is not None:
            installment = int(total_cost) / 12
            installment_per_month = round(installment, 2)
            if installment_per_month > 1000:
                installment = 1000
                month = round(total_month_from_joing / 12)
                due_float = total_cost - (months * installment)
                due = round(due_float, 2)
                paid_amount_float = total_cost - due
                paid_amount = round(paid_amount_float, 2)
                employee_total_tour_allowance_per_year = int(
                    total_months * employee_tour_allowance_per_year
                )
                remain_amount_after_paid_installment_float = (
                    employee_total_tour_allowance_per_year - paid_amount
                )
                remain_amount_after_paid_installment = round(
                    remain_amount_after_paid_installment_float, 2
                )
                htmt_content = html_template.render(
                    {
                        "obj": obj,
                        "total": total_cost,
                        "installment_per_month": installment,
                        "due": due,
                        "paid_amount": paid_amount,
                        "total_tour_allowance": remain_amount_after_paid_installment,
                    }
                )
                return format_html(htmt_content)
            month = round(total_month_from_joing / 12)
            due_float = total_cost - (months * installment)
            due = round(due_float, 2)
            paid_amount_float = total_cost - due
            paid_amount = round(paid_amount_float, 2)
            employee_total_tour_allowance_per_year = int(
                total_months * employee_tour_allowance_per_year
            )
            remain_amount_after_paid_installment_float = (
                employee_total_tour_allowance_per_year - paid_amount
            )
            remain_amount_after_paid_installment = round(
                remain_amount_after_paid_installment_float, 2
            )
            htmt_content = html_template.render(
                {
                    "obj": obj,
                    "total": total_cost,
                    "installment_per_month": installment_per_month,
                    "due": due,
                    "paid_amount": paid_amount,
                    "total_tour_allowance": remain_amount_after_paid_installment,
                }
            )
            return format_html(htmt_content)
        employee_total_tour_allowance_per_year = int(
            total_months * employee_tour_allowance_per_year
        )
        htmt_content = html_template.render(
            {
                "obj": "N/A",
                "total": "N/A",
                "installment_per_month": "N/A",
                "due": "N/A",
                "paid_amount": "N/A",
                "total_tour_allowance": employee_total_tour_allowance_per_year,
            }
        )
        return format_html(htmt_content)

    def leave_info(self, obj: Employee):
        html_template = get_template("admin/employee/list/leave_info.html")
        html_content = html_template.render(
            {
                "casual_passed": obj.leave_passed("casual"),
                "casual_remain": obj.leave_available("casual_leave"),
                "medical_passed": obj.leave_passed("medical"),
                "medical_remain": obj.leave_available("medical_leave"),
                "non_paid": obj.leave_passed("non_paid"),
                "employee": obj,
            }
        )
        return format_html(html_content)

    @admin.display(description="total compensation")
    def salary_history(self, obj):
        history = ""
        for salary in obj.salaryhistory_set.order_by("-active_from").all():
            history += f"<b>{intcomma(salary.payable_salary + 3000)}</b> ({naturalday(salary.active_from)}) <br>"
        return format_html(history)

    @admin.display(ordering="active", description="Status")
    def permanent_status(self, obj):
        return format_html(
            f'Active : {"<img src=/static/admin/img/icon-yes.svg />" if obj.active else "<img src=/static/admin/img/icon-no.svg />"} <br>'
            f'Permanent : {"<img src=/static/admin/img/icon-yes.svg />" if obj.permanent_date else "<img src=/static/admin/img/icon-no.svg />"}'
        )

    @admin.display(ordering="employeeskill__skill")
    def skill(self, obj):
        skill = ""
        for employee_skill in obj.employeeskill_set.all():
            skill += (
                f"{employee_skill.skill.title} - {employee_skill.percentage}% </br>"
            )
        return format_html(skill)

    def sum_total_leave(self, obj):
        total = obj.aggregate(total=Sum("total_leave"))["total"]
        if total is None:
            return 0
        return total
