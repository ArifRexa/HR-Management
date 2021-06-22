from django.db.models import Sum
from django.utils.html import format_html


class EmployeeAdmin:
    def employee_info(self, obj):
        return format_html(
            f"<dl>"
            f"<dt>Name</dt>  <dd>: {obj.full_name}</dd>"
            f"<dt>Designation</dt> <dd>: {obj.designation} {'*' if obj.manager else ''}</dd>"
            f"<dt>Joining Date</dt> <dd>: {obj.joining_date}</dd>"
            f"<dt>Resigned Date</dt> <dd>: {obj.resignation_set.filter(status='approved').first().date if obj.resignation_set.all() else ''}  "
            f"</dl>"
        )

    def leave_info(self, obj):
        approved_leave = obj.leave_set.filter(status='approved')
        return format_html(
            f"<dl>"
            f"<dt>Casual</dt>  <dd>{self.sum_total_leave(approved_leave.filter(leave_type='casual'))}/{obj.leave_management.casual_leave}</dd>"
            f"<dt>Medical</dt>  <dd>{self.sum_total_leave(approved_leave.filter(leave_type='medical'))}/{obj.leave_management.medical_leave}</dd>"
            f"<dt>Non Paid</dt>  <dd>{self.sum_total_leave(approved_leave.filter(leave_type='non_paid'))}</dd>"
            f"</dl>"
        )

    def salary_history(self, obj):
        if obj.salaryhistory_set.count() > 0:
            history = obj.salaryhistory_set.order_by('-id')[:2]
            return format_html(
                f"<dl>"
                f"<dt>Current Salary</dt>  <dd>{history[0].payable_salary} - {history[0].active_from}</dd>"
                f"<dt>Last Salary</dt>  <dd>{history[1].payable_salary if len(history) > 1 else '--'}</dd>"
                f"</dl>"
            )
        return 'Salary History Not Found'

    def sum_total_leave(self, obj):
        return obj.aggregate(total=Sum('total_leave'))['total']

    def print_appointment_latter(self, request, queryset):
        pass

    def increment_latter(self, request, queryset):
        pass
