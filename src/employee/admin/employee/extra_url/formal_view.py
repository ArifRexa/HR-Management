import datetime
from decimal import Decimal
import functools
import operator
from django.db.models.functions import ExtractMonth, ExtractYear, Least
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q, Case, When, Value, Count, Max, Subquery, OuterRef, Sum, F
from django.template.response import TemplateResponse
from django.utils import timezone

from account.models import Loan
from employee.models import Employee, Leave
from employee.models.employee import LateAttendanceFine, Observation

from project_management.models import Project
from django.db.models import OuterRef, Sum, Count, Case, When, Value, IntegerField

class FormalView(admin.ModelAdmin):
    def notice_bord(self, request, *args, **kwargs):
        nearby_summery = EmployeeNearbySummery()
        print(nearby_summery.employees_on_leave_today())
        context = dict(
            title="Notice Board",
            birthday=nearby_summery.birthdays(),
            anniversaries=nearby_summery.anniversaries(),
            # employee_on_leave_today=nearby_summery.employee_on_leave_today()
        )
        return TemplateResponse(
            request, "admin/employee/notice_board.html", context=context
        )

    def formal_summery_view(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.has_perm(
            "employee.can_see_formal_summery_view"
        ):
            raise PermissionDenied
        nearby_summery = EmployeeNearbySummery()
        context = dict(
            self.admin_site.each_context(request),
            title="Employee Calender",
            birthday=nearby_summery.birthdays(),
            permanent=nearby_summery.permanents,
            increment=nearby_summery.increments(),
            # salary_change=nearby_summery.last_salary_change(),
            anniversaries=nearby_summery.anniversaries(),
        )
        return TemplateResponse(
            request, "admin/employee/formal_summery.html", context=context
        )

    def observe_new_employee(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.has_perm(
            "employee.can_see_formal_summery_view"
        ):
            raise PermissionDenied
        nearby_summery = EmployeeNearbySummery()
        context = dict(
            self.admin_site.each_context(request),
            title="Observations",
            birthday=nearby_summery.birthdays(),
            permanent=nearby_summery.permanents,
            increment=nearby_summery.increments(),
            # salary_change=nearby_summery.last_salary_change(),
            anniversaries=nearby_summery.anniversaries(),
            new_employees=nearby_summery.new_employee(),
            new_proejcts=nearby_summery.new_projects(),
        )
        return TemplateResponse(
            request, "admin/employee/new_employee.html", context=context
        )

    def salary_receive_history_view(self, request, *args, **kwargs):
        employee_id = kwargs.get("employee_id__exact")

        if not request.user.is_superuser and request.user.employee.id != employee_id and not request.user.has_perm("employee.can_see_salary_receive_history"):
            raise PermissionDenied

        employee = Employee.objects.get(id=employee_id)

        #Calculate Late Attendance Fine
        # late_fine_subquery = LateAttendanceFine.objects.filter(
        #         employee_id=OuterRef('employee_id'),  # Match employee
        #         date__month=OuterRef('month')  # Match month of late fine and salary sheet
        #         ).values('employee_id').annotate(
        #             total_fine=Sum('total_late_attendance_fine')
        #         ).values('total_fine')
        

        late_fine_subquery = LateAttendanceFine.objects.filter(
                employee_id=OuterRef('employee_id'),  # Match employee
                date__month=OuterRef('month')  # Match month of late fine and salary sheet
                ).values('employee_id').annotate(
                late_count=Count('id'),  # Count late entries
                total_fine=Case(
                    # If late_count > 3, calculate fine
                    When(late_count__gt=3, then=Case(
                        # For 4th to 6th late entries: min(late_count, 6) - 3 * 80
                        When(late_count__lte=6, then=(Least(Value(6), F('late_count')) - Value(3)) * Value(80.00)),
                        # For 7th and above: (min(late_count, 6) - 3) * 80 + (late_count - 6) * 500
                        When(late_count__gt=6, then=((Least(Value(6), F('late_count')) - Value(3)) * Value(80.00)) + ((F('late_count') - Value(6)) * Value(500.00))),
                        output_field=IntegerField()
                    )),
                    # If late_count <= 3, no fine
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).values('total_fine')
        
        #Calculate Salary Loan
        salary_loan_subquery = Loan.objects.filter( 
            employee_id = OuterRef('employee_id'),
            loan_type = 'salary',
            start_date__month = OuterRef('month'),
            end_date__month = OuterRef('month')

        ).values('employee_id').annotate(
            total_loan = Sum('emi')
        ).values('total_loan')

        employee_salaries = (
            employee.employeesalary_set.filter(employee_id__exact=employee_id)
            .annotate(
                month = ExtractMonth('salary_sheet__date'),
                total_fine=Subquery(late_fine_subquery, output_field=models.DecimalField()),
                salary_loan = Subquery(salary_loan_subquery,output_field=models.DecimalField())
            )
            .order_by("-id")
        )
        for e in employee_salaries:
            print(e.salary_loan)

        employee_festival_bonuses = employee.employeefestivalbonus_set.filter(
            employee_id__exact=employee_id
        ).order_by("-id")

        context = dict(
            self.admin_site.each_context(request),
            employee=employee,
            employee_salaries=employee_salaries,
            employee_festival_bonuses=employee_festival_bonuses,
        )
        return TemplateResponse(
            request, "admin/employee/paid_salary_history.html", context=context
        )


class EmployeeNearbySummery:
    """
    Employee nearby summery class
    will return birthdays, permanents, salary change list, and employee to have an increment nearby
    """

    def __init__(self):
        self.today = datetime.datetime.today()
        self.employees = Employee.objects.filter(active=True)
        self.projects = Project.objects.filter(active=True)

    def birthdays(self):
        now = datetime.datetime.now()
        then = now + datetime.timedelta(days=31)

        monthdays = [(now.month, now.day)]
        while now <= then:
            monthdays.append((now.month, now.day))
            now += datetime.timedelta(days=1)

        monthdays = (
            dict(zip(("date_of_birth__month", "date_of_birth__day"), t))
            for t in monthdays
        )

        query = functools.reduce(operator.or_, (Q(**d) for d in monthdays))

        # TODO: Improve Query Performance
        return (
            self.employees.filter(query)
            .annotate(
                year_change=Case(
                    When(
                        date_of_birth__month__lt=datetime.datetime.now().date().month,
                        then=Value(1),
                    ),
                    default=Value(0),
                    output_field=models.IntegerField(),
                )
            )
            .order_by("year_change", "date_of_birth__month", "date_of_birth__day")
        )

    def permanents(self):
        qs = (
            self.employees.filter(
                permanent_date__isnull=True,
                active=True,
                joining_date__lte=(datetime.date.today() - datetime.timedelta(days=80)),
            )
            .order_by("joining_date")
            .values("full_name")
        )
        return qs, qs.count()

    def increments(self):
        qs = self.employees.annotate(
            salaryhistory_count=Count("salaryhistory"),
            current_salary_active_from=Max("salaryhistory__active_from"),
        ).filter(
            salaryhistory_count__gte=0,
            current_salary_active_from__lte=(self.today - datetime.timedelta(days=180)),
        )
        return qs

    def last_salary_change(self):
        salary_increment_list = []
        for inc_salary_list in self.employees.all():
            if (
                inc_salary_list.current_salary.active_from
                >= (self.today - datetime.timedelta(days=29)).date()
                and inc_salary_list.current_salary.active_from
                <= (self.today + datetime.timedelta()).date()
            ):
                salary_increment_list.append(inc_salary_list)
        return salary_increment_list

    # def anniversaries(self):
    #     qs = self.employees.filter(
    #         joining_date__month__in=[self.today.month, self.today.month + 1],
    #         permanent_date__isnull=False,
    #     ).values("full_name")
    #     return qs, qs.count()

    def employee_leave_nearby(self):
        qs = Leave.objects.filter(
            end_date__gte=self.today, status="approved"
        ).select_related("employee")
        return qs, qs.count()

    def employees_on_leave_today(self):
        return self.employees.filter(
            leave__start_date__gte=self.today,
            leave__end_date__lte=self.today,
            leave__status="approved",
        )

    def employees_birthday_today(self):
        return self.employees.filter(date_of_birth=timezone.now().date())

    def new_employee(self):
        return self.employees.filter(
            joining_date__gte=timezone.now() - datetime.timedelta(weeks=2)
        )

    def new_projects(self):
        return self.projects.filter(
            created_at__gte=timezone.now() - datetime.timedelta(weeks=2)
        )
        # return self.employees.filter(id==1)

    def new_lead_or_manager(self):
        new_lead_or_managers = Observation.objects.filter(
            created_at__gte=timezone.now() - datetime.timedelta(weeks=2)
        )
        return new_lead_or_managers
