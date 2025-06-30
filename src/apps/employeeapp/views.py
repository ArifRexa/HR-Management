import datetime, bisect
from dateutil import relativedelta
from calendar import month_abbr
from django.db import connection
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, views
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.employeeapp.filters import EmployeeFilter
from apps.employeeapp.permissions import HasConferenceRoomBookPermission, IsLeaveEditable, IsSuperUserOrReadOnly
from apps.mixin.views import BaseModelViewSet
from asset_management.models.credential import Credential, CredentialCategory
from employee.models.employee import BookConferenceRoom, Employee, LateAttendanceFine
from employee.models.employee_activity import EmployeeAttendance
from employee.models.employee_skill import EmployeeSkill
from django.db.models import (
    Prefetch, functions, Sum, Q,
    Value, Case, When, CharField,
    Count, Avg, F,
)
from django.db.models.functions import Concat
from django.utils import timezone

from employee.models.leave.leave import Leave
from project_management.models import EmployeeProjectHour
from .serializers import (
    BaseLeaveModelSerializer,
    EmployeeAttendanceSerializer,
    BaseBookConferenceRoomCreateModelSerializer, 
    BookConferenceRoomListModelSerializer,
    CreateUpdateCredentialModelSerializer,
    CredentialCategoryModelSerializer,
    CredentialModelSerializer,
    IdListSerializer,
    DashboardSerializer,
    DetailsCredentialModelSerializer, EmployeeBirthdaySerializer,
    EmployeeInfoSerializer, 
    EmployeeSerializer,
    LateAttendanceFineModelSerializer,
    LeaveModelSerializer,
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
        HasConferenceRoomBookPermission,
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


class CredentialViewSetView(BaseModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperUserOrReadOnly,
    ]
    search_fields  = [
        "title", "description",
        "privileges__employee__full_name",
    ]
    filterset_class = None
    filterset_fields = [
        "status",
    ]
    serializer_class = CredentialModelSerializer
    serializers = {
        "credential_status_update": IdListSerializer,
        "delete_credentials": IdListSerializer,
        "create": CreateUpdateCredentialModelSerializer,
        "update": CreateUpdateCredentialModelSerializer,
        "partial_update": CreateUpdateCredentialModelSerializer,
        "retrieve": DetailsCredentialModelSerializer,
    }
    queryset = Credential.objects.select_related(
        "category",
        "created_by",
    ).prefetch_related(
        "privileges"
    ).annotate(
        total_privilege=Count("privileges")
    ).all()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser is False and user.has_perm(
            "asset_management.access_all_credentials"
        ) is False :
            return super().get_queryset().filter(privileges__in=[user])
        return super().get_queryset()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="status",
                in_=openapi.IN_QUERY,
                description="Credential status update.",
                type=openapi.TYPE_STRING,
                enum=[ item[0]
                    for item in Credential.STATUS_CHOICES
                ],
                required=True,
            )
        ]
    )
    @action(detail=False, methods=['patch'])
    def credential_status_update(self, request):
        """
        Bulk status update multiple Credential instances.

        This endpoint accepts a PATCH request with a JSON body containing
        a list of credential IDs to update status.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.get_queryset().filter(
            id__in=serializer.validated_data.get("ids")
        ).update(
            status=request.query_params.get("status")
        )
        return Response(data={"result": "Credential status update successfull."})


    @action(detail=False, methods=["post"])
    def delete_credentials(self, request):
        """
        Bulk delete multiple Credential instances.

        This endpoint accepts a POST request with a JSON body containing
        a list of credential IDs to delete.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.get_queryset().filter(
            id__in=serializer.validated_data.get("ids")
        ).delete()
        return Response(data={"result": "Credentials delete successfull."})


class CredentialCategoryViewSet(BaseModelViewSet):

    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperUserOrReadOnly,
    ]
    queryset = CredentialCategory.objects.all()
    serializer_class = CredentialCategoryModelSerializer

    search_fields = [
        "title", "description",
    ]


class EmployeeAttendanceListView(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = Employee.objects.all()
    serializer_class = EmployeeAttendanceSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            data = self.process_attendance_data(page)
            serializer = self.get_serializer(data, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return serializer
    
    def get_dates(self):
        """
        return a list of dates from one month ago up to the current date.
        """
        current_time = timezone.now()
        previous_date = (current_time - relativedelta.relativedelta(months=1))
        # dates = []
        # while previous_date <= current_time:
        #     # if previous_date.date().weekday() < 5:
        #     #     dates.append(previous_date.date())
        #     dates.append(previous_date.date().isoformat())
        #     previous_date += datetime.timedelta(days=1)
        
        dates = [
            (previous_date + datetime.timedelta(days=i)).date().isoformat() for i in range((current_time - previous_date).days + 1)
        ]
        return dates

    def process_attendance_data(self, page):
        """
        process and return employee list data with last one month attentance.
        """
        dates = self.get_dates()
        current_date_time = timezone.now()
        current_date =  current_date_time.date()
        one_month_ago_date = (current_date_time - relativedelta.relativedelta(months=1)).date()
        employee_queryset = Employee.objects.filter(
            id__in=[employe.id for employe in page]
        ).prefetch_related(
            Prefetch(
                "employeeattendance_set",
                queryset=EmployeeAttendance.objects.filter(
                    date__gte=one_month_ago_date,
                ).prefetch_related("employeeactivity_set")
            ),
            Prefetch(
                "employeeprojecthour_set",
                queryset=EmployeeProjectHour.objects.filter(
                    created_at__date__gte=one_month_ago_date,
                ),
            )
        ).annotate(
            late_count=Count(
                "employeeattendance__id",
                distinct=True,
                filter=Q(
                    employeeattendance__date__year=current_date.year,
                    employeeattendance__date__month=current_date.month,
                    employeeattendance__entry_time__gt=datetime.time(11, 10),
                )
            ),
            # total_project_hour=Sum(
            #     "employeeprojecthour__hours",
            #     distinct=True,
            #     filter=Q(
            #         employeeprojecthour__created_at__date__gte=one_month_ago_date,
            #     )
            # ),
            # average_project_hour=Avg(
            #     "employeeprojecthour__hours",
            #     filter=Q(
            #         employeeprojecthour__created_at__date__gte=one_month_ago_date,
            #     )
            # ),
            total_attend_in_day=Count(
                "employeeattendance__id",
                distinct=True,
                filter=Q(
                    employeeattendance__date__gte=one_month_ago_date,
                )
            )
        )

        employee_list = []
        for employe in employee_queryset:
            employe_dict = {
                "id": employe.id,
                "full_name": employe.full_name,
                "image": employe.image,
                "late_count": employe.late_count,
                # "average_project_hour": employe.average_project_hour,
                # "total_project_hour": employe.total_project_hour,
                "total_attend_in_day": employe.total_attend_in_day,
                "total_inside_office_in_secends": None,
                "attendance": [],
            }
            employee_attendances = [
                {
                    "id": None,
                    "date": date,
                    "entry_time": None,
                    "exit_time": None,
                    "created_at": None,
                    "inside_office_in_secends": None,
                    "outside_office_in_secends": None,
                } for date in dates
            ]
            total_inside_in_secends = 0
            for employeeattendance in employe.employeeattendance_set.all():
                attendance = {
                    "id": employeeattendance.id,
                    "entry_time": None,  # employeeattendance.entry_time,
                    "exit_time": None,
                    "created_at": employeeattendance.created_at,
                    "inside_office_in_secends": None,
                    "outside_office_in_secends": None,
                }
                inside_office_in_secends = 0
                current_date_time = datetime.datetime.now()
                for employee_activity in employeeattendance.employeeactivity_set.all():
                    attendance["entry_time"] = attendance["entry_time"] or employee_activity.start_time
                    attendance["exit_time"] = employee_activity.end_time
                    inside_office_in_secends += ((employee_activity.end_time or current_date_time) - employee_activity.start_time).total_seconds()
                inside_office_in_secends = int(inside_office_in_secends)
                total_inside_in_secends += inside_office_in_secends
                office_exit_time = attendance["exit_time"] or current_date_time
                office_entry_time = attendance["entry_time"] or current_date_time
                total_entry_exit_in_secends = int((office_exit_time - office_entry_time).total_seconds())

                attendance["inside_office_in_secends"] = inside_office_in_secends
                attendance["outside_office_in_secends"] = total_entry_exit_in_secends - inside_office_in_secends
                attendance_index = bisect.bisect_left(dates, employeeattendance.created_at.date().isoformat())
                employee_attendances[attendance_index].update(attendance)
            employe_dict["total_inside_office_in_secends"] = total_inside_in_secends
            employe_dict["attendance"] = employee_attendances

            employee_list.append(employe_dict)
        
        return employee_list


class EmployeeLateAttendanceFine(ListAPIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = LateAttendanceFineModelSerializer

    queryset = LateAttendanceFine.objects.select_related("employee").order_by("-id")

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.employee.operation:
            return queryset
        return queryset.filter(employee=user.employee)


class EmployeeLeaveView(BaseModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        IsLeaveEditable,
    ]
    filterset_class = None
    filterset_fields = [
        "status",
        "leave_type",
        "applied_leave_type",
    ]
    queryset = Leave.objects.select_related(
        "employee",
    ).prefetch_related(
        "leaveattachment_set"
    ).all()
    serializers = {
        "create": BaseLeaveModelSerializer,
        "update": BaseLeaveModelSerializer,
        "partial_update": BaseLeaveModelSerializer,
        "leave_status_update_or_delete": IdListSerializer,
    }
    serializer_class = LeaveModelSerializer

    @swagger_auto_schema(
        request_body=IdListSerializer,
        manual_parameters=[
            openapi.Parameter(
                name="action_by",
                in_=openapi.IN_QUERY,
                description="Leaves status update or delete",
                required=True,
                type=openapi.TYPE_STRING,
                enum=[
                    "approved", "rejected",
                    "delete",
                ]
            )
        ]
    )
    @action(methods=["post"], detail=False)
    def leave_status_update_or_delete(self, request):
        """
        Leave status updated or delete Leave based on the 'action_by' value.
        """
        query_param = request.query_params.get("action_by")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        filtered_queryset = super().get_queryset().filter(id__in=serializer.validated_data.get("ids"))
        if query_param == "delete":
            filtered_queryset.delete()
            return Response(data={"result": "Leaves delete successfull."})
        elif query_param == "approved":
            filtered_queryset.update(status="approved")
        elif query_param == "rejected":
            filtered_queryset.update(status="rejected")
        return Response(data={"result": "Leave status updated"})
