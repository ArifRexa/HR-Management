import datetime

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils import timezone

from employee.models import Employee, Leave


class FormalView(admin.ModelAdmin):

    def notice_bord(self, request, *args, **kwargs):
        nearby_summery = EmployeeNearbySummery()
        print(nearby_summery.employees_on_leave_today())
        context = dict(
            title='Notice Board',
            birthday=nearby_summery.birthdays(),
            anniversaries=nearby_summery.anniversaries(),
            # employee_on_leave_today=nearby_summery.employee_on_leave_today()
        )
        return TemplateResponse(request, "admin/employee/notice_board.html", context=context)

    def formal_summery_view(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        nearby_summery = EmployeeNearbySummery()
        context = dict(
            self.admin_site.each_context(request),
            title='Employee Calender',
            birthday=nearby_summery.birthdays(),
            permanent=nearby_summery.permanents,
            increment=nearby_summery.increments(),
            anniversaries=nearby_summery.anniversaries()
        )
        return TemplateResponse(request, "admin/employee/formal_summery.html", context=context)

    def salary_receive_history_view(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.employee.id != kwargs.get(*kwargs):
            raise PermissionDenied

        employee = Employee.objects.get(id=kwargs.get(*kwargs))
        employee_salaries = employee.employeesalary_set.filter(employee_id__exact=kwargs.get(*kwargs)).order_by('-id')
        context = dict(
            self.admin_site.each_context(request),
            employee=employee,
            employee_salaries=employee_salaries
        )
        return TemplateResponse(request, "admin/employee/paid_salary_history.html", context=context)


class EmployeeNearbySummery:
    """
    Employee nearby summery class
    will return birthdays, permanents, and employee to have an increment nearby
    """

    def __init__(self):
        self.today = datetime.datetime.today()
        self.employees = Employee.objects.filter(active=True)

    def birthdays(self):
        return self.employees.extra(
            select={'birth_month': 'month(date_of_birth)', 'birth_day': 'day(date_of_birth)'}).filter(
            date_of_birth__month__gte=timezone.now().date().month,
            date_of_birth__month__lte=(datetime.datetime.now() + datetime.timedelta(days=30)).month
        ).order_by('birth_month', 'birth_day')

    def permanents(self):
        return self.employees.filter(
            permanent_date__isnull=True,
            active=True,
            joining_date__lte=(datetime.date.today() - datetime.timedelta(days=80))
        ).order_by('joining_date')

    def increments(self):
        increment_employee = []
        for inc_employee in self.employees.all():
            if inc_employee.salaryhistory_set.count() > 0 and inc_employee.current_salary.active_from <= (
                    self.today - datetime.timedelta(days=150)).date():
                increment_employee.append(inc_employee)
        return increment_employee

    def anniversaries(self):
        return self.employees.filter(
            joining_date__month__in=[self.today.month, self.today.month + 1],
            permanent_date__isnull=False
        )

    def employees_on_leave_today(self):
        return self.employees.filter(
            leave__start_date__gte=self.today,
            leave__end_date__lte=self.today,
            leave__status='approved'
        )

    def employees_birthday_today(self):
        return self.employees.filter(date_of_birth=timezone.now().date())
