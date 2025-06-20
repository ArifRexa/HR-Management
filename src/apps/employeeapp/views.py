import datetime
from calendar import month_abbr
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, views
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.response import Response

from apps.employeeapp.filters import EmployeeFilter
from apps.mixin.views import BaseModelViewSet
from employee.models.employee import BookConferenceRoom, Employee
from employee.models.employee_skill import EmployeeSkill
from django.db.models import (
    Prefetch, functions, Sum, Q,
    Value, Case, When, CharField,
)
from django.db.models.functions import Concat
from django.utils import timezone

from project_management.models import EmployeeProjectHour
from .serializers import (
    BaseBookConferenceRoomCreateModelSerializer, 
    BookConferenceRoomListModelSerializer,
    DashboardSerializer, EmployeeBirthdaySerializer, 
    EmployeeSerializer,
)


class EmployeeViewSet(BaseModelViewSet):
    queryset = (
        Employee.objects.select_related("user", "user__profile", "user__userlogs", "designation")
        .prefetch_related(
            "leave_set",
            "dailyprojectupdate_employee",
            "dailyprojectupdate_manager",
            Prefetch("employeeskill_set", queryset=EmployeeSkill.objects.select_related("skill").all()),
        )
        .order_by("id")
    )
    filterset_class = EmployeeFilter
    serializer_class = EmployeeSerializer
    search_fields = ["full_name", "user__email", "email"]
    
    

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "is_active",
                openapi.IN_QUERY,
                description="employee is active or not",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "is_permanent",
                openapi.IN_QUERY,
                description="employee is permanent or not",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "is_lead",
                openapi.IN_QUERY,
                description="employee is lead or not",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "is_manager",
                openapi.IN_QUERY,
                description="employee is manager or not",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "created_at_after",
                openapi.IN_QUERY,
                description="created_at from date",
                type=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "created_at_before",
                openapi.IN_QUERY,
                description="created_at to date",
                type=openapi.FORMAT_DATE,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class EmployeeDashboardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        employee = Employee.objects.get(user=request.user)
        serializer = DashboardSerializer(employee)
        return Response(serializer.data)


class EmployeeProjectHourStatisticView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="filter_by",
                in_=openapi.IN_QUERY,
                description="generate project hour stastics",
                enum=[
                    "monthly",
                    "yearly",
                ],
                type=openapi.TYPE_STRING,
                required=True,
            ) 
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        generate employee projects hour statistic based on a month or yearly.
        """
        filter_by = request.query_params.get("filter_by", "monthly")
        
        get_statistic_data = {
            "monthly": self.get_monthly_statistic,
            "yearly": self.get_yearly_statistic,
        }
        
        return Response(get_statistic_data.get(filter_by)(request))
    
    def get_monthly_statistic(self, request):
        current_time = timezone.now()
        employee_project_hours = EmployeeProjectHour.objects.filter(
            employee=request.user.employee,
            created_at__year=current_time.year,
        ).annotate(
            month=functions.ExtractMonth("created_at")
        ).values("month").annotate(
            total_hours=functions.Round(
                Sum("hours"),
                precision=2
            )
        ).order_by("month")
        employee_project_hours_dict = {
            employee_project_hour["month"]: employee_project_hour["total_hours"] for employee_project_hour in employee_project_hours
        }
        monthly_employee_project_hours = [
            {
                "month": month_abbr[month_number],
                "total_hours": employee_project_hours_dict.get(month_number, 0)
            }
            for month_number in range(1, 13)
        ]
        return monthly_employee_project_hours
    
    def get_yearly_statistic(self, request):
        employee_yearly_project_hours = EmployeeProjectHour.objects.filter(
            employee=request.user.employee,
        ).annotate(
            year=functions.ExtractYear("created_at")
        ).values("year").annotate(
            total_hours=functions.Round(
                Sum("hours"),
                precision=2
            )
        ).order_by("year")
        return employee_yearly_project_hours.values("year", "total_hours")

        
class NearByEmployeesBirthDayView(ListAPIView):
    
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = EmployeeBirthdaySerializer
    queryset = Employee.objects.filter(active=True)
    
    def get_queryset(self):
        current = now = datetime.datetime.now()
        then = now + datetime.timedelta(days=31)

        filters = Q()
        while now <= then:
            filters |= Q(date_of_birth__month=now.month, date_of_birth__day=now.day)
            now += datetime.timedelta(days=1)
        
        queryset =  super().get_queryset().filter(
            filters
        ).annotate(
            birth_day=Concat(
                Case(
                    When(
                        date_of_birth__month__lt=current.month,
                        then=Value(current.year+1)
                    ),
                    default=Value(current.year)
                ),
                Value('-'),
                "date_of_birth__month",
                Value('-'),
                "date_of_birth__day",
                output_field=CharField()
            )
        ).order_by("birth_day")
        return queryset


class BookConferenceRoomListCreateView(ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = BookConferenceRoomListModelSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BaseBookConferenceRoomCreateModelSerializer
        return super().get_serializer_class()

    queryset = BookConferenceRoom.objects.filter(
        created_at__date=datetime.datetime.today().date()
    ).select_related(
        "manager_or_lead",
    ).order_by("start_time")
