import datetime
import functools
import operator

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q, Case, When, Value, Count, Max
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
        if not request.user.is_superuser and not request.user.has_perm("employee.can_see_formal_summery_view"):
            raise PermissionDenied
        nearby_summery = EmployeeNearbySummery()
        context = dict(
            self.admin_site.each_context(request),
            title='Employee Calender',
            birthday=nearby_summery.birthdays(),
            permanent=nearby_summery.permanents,
            increment=nearby_summery.increments(),
            salary_change=nearby_summery.last_salary_change(),
            anniversaries=nearby_summery.anniversaries()
        )
        return TemplateResponse(request, "admin/employee/formal_summery.html", context=context)

    def salary_receive_history_view(self, request, *args, **kwargs):
        employee_id = kwargs.get('employee_id__exact')
        
        if not request.user.is_superuser and request.user.employee.id != employee_id:
            raise PermissionDenied
        
        employee = Employee.objects.get(id=employee_id)
        
        employee_salaries = employee.employeesalary_set.filter(employee_id__exact=employee_id).order_by('-id')
        employee_festival_bonuses = employee.employeefestivalbonus_set.filter(employee_id__exact=employee_id).order_by('-id')
        
        context = dict(
            self.admin_site.each_context(request),
            employee=employee,
            employee_salaries=employee_salaries,
            employee_festival_bonuses=employee_festival_bonuses,
        )
        return TemplateResponse(request, "admin/employee/paid_salary_history.html", context=context)


class EmployeeNearbySummery:
    """
    Employee nearby summery class
    will return birthdays, permanents, salary change list, and employee to have an increment nearby
    """

    def __init__(self):
        self.today = datetime.datetime.today()
        self.employees = Employee.objects.filter(active=True)


    def birthdays(self):
        now = datetime.datetime.now()
        then = now + datetime.timedelta(days=31)

        monthdays = [(now.month, now.day)]
        while now <= then:
            monthdays.append((now.month, now.day))
            now += datetime.timedelta(days=1)

        monthdays = (dict(zip(("date_of_birth__month", "date_of_birth__day"), t)) 
                    for t in monthdays)

        query = functools.reduce(operator.or_, (Q(**d) for d in monthdays))

        # TODO: Improve Query Performance
        return self.employees.filter(query).annotate(
            year_change=Case(
                When(date_of_birth__month__lt=datetime.datetime.now().date().month, then=Value(1)),
                default=Value(0),
                output_field=models.IntegerField()
            )
        ).order_by('year_change', 'date_of_birth__month', 'date_of_birth__day')

    def permanents(self):
        return self.employees.filter(
            permanent_date__isnull=True,
            active=True,
            joining_date__lte=(datetime.date.today() - datetime.timedelta(days=80))
        ).order_by('joining_date')

    def increments(self):
        qs = self.employees.annotate(
            salaryhistory_count=Count("salaryhistory"),
            current_salary_active_from=Max('salaryhistory__active_from'),
        ).filter(
            salaryhistory_count__gte=0,
            current_salary_active_from__lte=(self.today-datetime.timedelta(days=120)),
        )
        return qs
    

    def last_salary_change(self):
        salary_increment_list = []
        for inc_salary_list in self.employees.all():
            if inc_salary_list.current_salary.active_from >= (
                    self.today - datetime.timedelta(days=29)).date() and inc_salary_list.current_salary.active_from <= (
                    self.today + datetime.timedelta()).date():
                salary_increment_list.append(inc_salary_list)
        return salary_increment_list

    def anniversaries(self):
        return self.employees.filter(
            joining_date__month__in=[self.today.month, self.today.month + 1],
            permanent_date__isnull=False
        )

    def employee_leave_nearby(self):
        qs = Leave.objects.filter(
            end_date__gte=self.today,
            status='approved'
        ).select_related('employee')
        return qs, qs.count()

    def employees_on_leave_today(self):
        return self.employees.filter(
            leave__start_date__gte=self.today,
            leave__end_date__lte=self.today,
            leave__status='approved'
        )

    def employees_birthday_today(self):
        return self.employees.filter(date_of_birth=timezone.now().date())
